import { useEffect, useRef } from 'react'
import { useSession } from '../store/SessionStore'
import { useAgentActions } from '../lib/useAgentActions'

/**
 * One persistent dispatcher for the whole OS shell.
 *
 * It lives above the routed canvas, so route changes never remount it and
 * never replay actions from conversation history. Navigation is automatic
 * once per assistant message, which is what makes canvas takeover feel
 * native instead of asking the learner to confirm.
 */
export function AgentActionController() {
  const { messages } = useSession()
  const runAction = useAgentActions()
  const executed = useRef(new Set<string>())

  useEffect(() => {
    for (const message of messages) {
      if (message.role !== 'assistant' || !message.actions?.length) continue
      if (executed.current.has(message.id)) continue
      executed.current.add(message.id)
      for (const action of message.actions) {
        // The reading page can consume both; REVEAL is last in diagnosis and
        // its showAnalysis path also exposes the source sentence highlight.
        runAction(action)
      }
    }
  }, [messages, runAction])

  return null
}
