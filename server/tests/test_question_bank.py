"""Question-bank lifecycle and student isolation; no real model, network or app.db."""
import copy
import json
import sqlite3
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import app as api
from db import SCHEMA, migrate_schema
from question_bank import (BankError, export_entry, generate_analysis, import_batch,
                           readiness, transition)
from tools import get_question, get_sentence, list_questions, list_sentences, search_past_exams, get_meta
from workflows import _context, run_options_workflow, run_sentence_workflow


def document(year=2025, complete=True):
    passage = "People can learn English through regular reading and careful practice. Reliable feedback helps learners understand their mistakes."
    qs=[]
    for n in range(21,26):
        q={"number":n,"question_type":"细节题","content":f"What does the author suggest in question {n}?",
           "options":{k:f"Option {k}" for k in "ABCD"},"correct_answer":"A",
           "answer_source":"provided","answer_source_note":"Synthetic test key, manually checked for this fixture",
           "source_quote":"People can learn English through regular reading and careful practice.","evidence_note":""}
        if complete:
            q["analysis"]={k:{"trapType":"正确" if k=="A" else "无中生有","explanation":f"Fixture explanation for {k}"} for k in "ABCD"}
            q["steps"]=["Read the passage.","Compare the options."]
        qs.append(q)
    return {"format":"kaoyan-question-bank-v1","passages":[{"year":year,"exam_type":"英语一","text_number":1,
            "source_note":"Synthetic fixture, not a real examination", "paragraphs":[passage],"questions":qs}]}


class BankTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(":memory:",check_same_thread=False)
        self.conn.row_factory=sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        migrate_schema(self.conn)
        self.conn.commit()
        self.addCleanup(self.conn.close)

    def put(self,doc=None):
        result=import_batch(self.conn,doc or document(),"tester")
        self.assertTrue(result["ok"],result)
        return result["results"][0]["passage_id"]

    def publish(self,pid):
        transition(self.conn,pid,1,"review","reviewer")
        return transition(self.conn,pid,2,"publish","publisher")

    def client(self):
        def override(): yield self.conn
        api.app.dependency_overrides[api.get_db]=override
        self.addCleanup(api.app.dependency_overrides.clear)
        client=TestClient(api.app)
        self.addCleanup(client.close)
        return client

    def test_draft_invisible_to_lists_getters_search_meta_and_context(self):
        pid=self.put()
        sid=self.conn.execute("SELECT id FROM exam_sentences LIMIT 1").fetchone()[0]
        qid=f"{pid}_q21"
        self.assertIsNone(get_question(self.conn,qid))
        self.assertIsNone(get_sentence(self.conn,sid))
        self.assertIsNotNone(get_question(self.conn,qid,include_drafts=True))
        self.assertEqual(list_questions(self.conn),[])
        self.assertEqual(list_sentences(self.conn),[])
        self.assertEqual(search_past_exams(self.conn,query="People")[0],[])
        self.assertEqual(_context(self.conn,pid),(None,[],[]))
        self.assertIsNone(run_options_workflow(self.conn,qid))
        self.assertIsNone(run_sentence_workflow(self.conn,sid))
        meta=get_meta(self.conn)
        self.assertEqual(meta["passage_count"],0)

    def test_review_then_publish_visibility_and_audit(self):
        pid=self.put()
        self.assertEqual(readiness(self.conn,pid),[])
        with self.assertRaises(BankError): transition(self.conn,pid,1,"publish","publisher")
        state=self.publish(pid)
        self.assertEqual(state["publication_status"],"published")
        self.assertEqual(state["revision"],3)
        self.assertEqual(len(list_questions(self.conn)),5)
        self.assertEqual(len(list_sentences(self.conn)),2)
        self.assertEqual(get_question(self.conn,f"{pid}_q21")["review_status"],"approved")
        actions=[r[0] for r in self.conn.execute("SELECT action FROM bank_events ORDER BY id")]
        self.assertEqual(actions,["imported","review","publish"])

    def test_practice_publication_allows_answers_without_claiming_reviewed_analysis(self):
        doc = document(complete=False)
        for q in doc['passages'][0]['questions']:
            q['source_quote'] = ''
        pid = self.put(doc)
        state = transition(self.conn, pid, 1, 'publish-practice', 'tester')
        self.assertEqual(state['publication_status'], 'published')
        self.assertEqual(state['reviewed_by'], '')
        self.assertEqual(get_question(self.conn, f'{pid}_q21')['review_status'], 'practice')
        self.assertEqual(get_meta(self.conn)['question_count'], 5)
        response = self.client().get('/api/questions/full')
        self.assertEqual(len(response.json()['items']), 5)
        self.assertEqual(response.json()['items'][0]['analysis'], {})
        result = self.client().post('/api/records', json={'question_id':f'{pid}_q21', 'question_type':'细节题', 'user_answer':'A', 'correct_answer':'B'})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json()['record']['isCorrect'])
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM practice_records').fetchone()[0], 1)

    def test_practice_publication_rejects_unknown_answers(self):
        doc = document(complete=False)
        doc['passages'][0]['questions'][0]['answer_source'] = 'unknown'
        pid = self.put(doc)
        with self.assertRaises(BankError):
            transition(self.conn, pid, 1, 'publish-practice', 'tester')
        self.assertEqual(get_meta(self.conn)['passage_count'], 0)

    def test_reviewer_checks_required_metadata_analysis_and_evidence(self):
        doc=document(complete=False)
        p=doc["passages"][0]
        p["source_note"]=""
        for q in p["questions"]:
            q["answer_source"]="inferred"
            q["source_quote"]=""
        pid=self.put(doc)
        issues=readiness(self.conn,pid)
        self.assertTrue(any("source_note" in i for i in issues))
        self.assertTrue(any("完整解析" in i for i in issues))
        self.assertTrue(any("evidence_note" in i for i in issues))
        with self.assertRaises(BankError): transition(self.conn,pid,1,"review","reviewer")
        self.assertEqual(self.conn.execute("SELECT publication_status FROM exam_passages").fetchone()[0],"draft")

    def test_full_passage_evidence_note_allows_human_review_without_fake_binding(self):
        doc=document()
        for q in doc["passages"][0]["questions"]:
            q["source_quote"]=""
            q["evidence_note"]="Whole paragraph: contrast regular reading with feedback; human checked."
        pid=self.put(doc)
        self.publish(pid)
        self.assertIsNone(get_question(self.conn,f"{pid}_q21")["source_sentence_id"])

    def test_update_keeps_question_ids_records_withdraws_and_invalidates_cache(self):
        pid=self.put()
        self.publish(pid)
        qid=f"{pid}_q21"
        self.conn.execute("INSERT INTO practice_records (question_id,question_type,user_answer,correct_answer,is_correct) VALUES (?,?,?,?,?)",(qid,"细节题","A","A",1))
        sid=self.conn.execute("SELECT id FROM exam_sentences LIMIT 1").fetchone()[0]
        self.conn.execute("INSERT INTO sentence_breakdowns (sentence_id,data_json) VALUES (?,?)",(sid,"{}"))
        self.conn.commit()
        doc=export_entry(self.conn,pid)
        doc["passages"][0]["questions"][0]["content"]="Corrected question content"
        result=import_batch(self.conn,doc,"editor",update=True)
        self.assertTrue(result["ok"],result)
        self.assertEqual(result["results"][0]["revision"],4)
        self.assertIsNone(get_question(self.conn,qid))
        self.assertEqual(self.conn.execute("SELECT question_id FROM practice_records").fetchone()[0],qid)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM sentence_breakdowns").fetchone()[0],0)
        self.assertEqual(get_question(self.conn,qid,include_drafts=True)["content"],"Corrected question content")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM exam_questions").fetchone()[0],5)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM bank_events WHERE action='before_update'").fetchone()[0],1)

    def test_stale_revision_and_duplicate_do_not_change_data(self):
        pid=self.put()
        duplicate=import_batch(self.conn,document(),"tester")
        self.assertFalse(duplicate["ok"])
        doc=export_entry(self.conn,pid)
        doc["passages"][0]["expected_revision"]=0
        self.assertFalse(import_batch(self.conn,doc,"editor",update=True)["ok"])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM exam_questions").fetchone()[0],5)
        with self.assertRaises(BankError): transition(self.conn,pid,0,"withdraw","editor")

    def test_batch_partial_success_has_per_item_errors(self):
        doc=document()
        bad=copy.deepcopy(doc["passages"][0])
        bad["year"]=2024
        bad["questions"][2]["options"].pop("D")
        doc["passages"].append(bad)
        result=import_batch(self.conn,doc,"tester")
        self.assertEqual((result["succeeded"],result["failed"]),(1,1))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM exam_passages").fetchone()[0],1)

    def test_write_failure_rolls_back_entire_passage(self):
        self.conn.executescript("CREATE TRIGGER stop BEFORE INSERT ON exam_questions WHEN NEW.number=23 BEGIN SELECT RAISE(ABORT,'fixture failure'); END;")
        result=import_batch(self.conn,document(),"tester")
        self.assertFalse(result["ok"])
        for table in ("exam_passages","exam_sentences","exam_questions","bank_events"):
            self.assertEqual(self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0],0)

    def test_analysis_generation_before_lock_atomic_and_revision_checked(self):
        pid=self.put(document(complete=False))
        def analyzer(passage,qs):
            self.assertFalse(self.conn.in_transaction)
            return {q["number"]:{"analysis":{k:{"trapType":"正确" if k=="A" else "无中生有","explanation":"Checked explanation"} for k in "ABCD"},"steps":["Compare with evidence"]} for q in qs}
        result=generate_analysis(self.conn,pid,1,"editor",analyzer)
        self.assertEqual(result["revision"],2)
        self.assertEqual(readiness(self.conn,pid),[])
        with self.assertRaises(BankError): generate_analysis(self.conn,pid,2,"editor",lambda p,qs:{})
        self.assertEqual(self.conn.execute("SELECT revision FROM exam_passages").fetchone()[0],2)
        transition(self.conn,pid,2,"review","reviewer")
        with self.assertRaises(BankError): generate_analysis(self.conn,pid,3,"editor",analyzer)

    def test_student_routes_reject_draft_ids_and_http_management(self):
        pid=self.put()
        sid=self.conn.execute("SELECT id FROM exam_sentences LIMIT 1").fetchone()[0]
        client=self.client()
        for path in ("/api/passages","/api/questions","/api/questions/full","/api/sentences"):
            response=client.get(path)
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json()["items"],[])
        self.assertEqual(client.get(f"/api/passages/{pid}/sentences").status_code,404)
        self.assertEqual(client.get(f"/api/sentences/{sid}/breakdown").status_code,404)
        self.assertEqual(client.post("/api/workflow/options",json={"question_id":f"{pid}_q21"}).status_code,404)
        self.assertEqual(client.post("/api/workflow/sentence",json={"sentence_id":sid}).status_code,404)
        self.assertEqual(client.post("/api/records",json={"question_id":f"{pid}_q21","question_type":"细节题","user_answer":"A","correct_answer":"A"}).status_code,404)
        self.assertEqual(client.post("/api/exams/auto-import",json={}).status_code,410)
        self.assertEqual(client.post("/api/exams/import",json={}).status_code,410)
        self.assertEqual(client.get("/api/agent/runs").status_code,410)
        self.publish(pid)
        self.assertEqual(len(client.get("/api/questions/full").json()["items"]),5)
        self.assertEqual(client.get(f"/api/passages/{pid}/sentences").status_code,200)
        transition(self.conn,pid,3,"withdraw","editor")
        self.assertEqual(client.get("/api/questions/full").json()["items"],[])

    def test_seed_placeholders_do_not_block_real_text_or_later_update(self):
        from seed import _seed_exams
        _seed_exams(self.conn)
        self.conn.commit()
        pid=self.put(document(year=2024))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM exam_passages").fetchone()[0],3)
        self.publish(pid)
        _seed_exams(self.conn)
        self.conn.commit()
        self.assertIsNotNone(get_question(self.conn,f"{pid}_q21"))
        result=import_batch(self.conn,export_entry(self.conn,pid),"editor",update=True)
        self.assertTrue(result["ok"],result)
        self.assertEqual(result["results"][0]["revision"],4)

    def test_record_grading_uses_saved_answer_not_client_claim(self):
        pid=self.put()
        self.publish(pid)
        response=self.client().post("/api/records",json={"question_id":f"{pid}_q21","question_type":"细节题","user_answer":"B","correct_answer":"B"})
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.json()["record"]["isCorrect"])


if __name__=="__main__": unittest.main()
