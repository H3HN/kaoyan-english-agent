# Question-bank audit

Human review items are obligations, not machine approval. Triage never suppresses findings or changes the source.

## Provenance

- source_kind: database
- source_path: D:\DSH\DSH Workplace\kaoyan-review-20261110\quality-restore-check.db
- source_sha256: 9bd17185c6cd9f091c49ab3b328d7de6c075b2334e98c20d36d21268939da94c
- normalized_rows_sha256: 33cd7ee631833a4e31479e6fb230162729b0530a9defa7381646139aaedb9f03
- code_revision: a530ebc669da505ff2a222ed146d3777b16a5665
- rule_version: bank-audit-1
- timestamp: 2026-11-10T08:45:44.609184+00:00
- code_sha256: {"bank_audit.py":"3554a0fb1566ade303f2b8e6960214328fed8c287244630d85b5ea51bcbe0e7b","exam_import.py":"80c5949414d7ce1e918d8655fa88986363b3492d4c05d5682aa8b90e21e051d8","scripts/audit_question_bank.py":"bc7fc106debc88841c14e19de918010306dae351eea08cf168e584f448eeaac9"}

## Summary

```json
{
  "passages": 72,
  "questions": 360,
  "sentences": 1362,
  "published_passages": 72,
  "deterministic_issue_count": 0,
  "human_review_item_count": 692
}
```

- source_capture: Raw main/WAL file hashes captured separately; normalized_rows_sha256 identifies the transaction-consistent logical snapshot. Use a quiescent backup for archival byte provenance.
- wal_sha256: none

## Previous-report comparison

### new (0)


### resolved (0)


### persistent (692)

- audit-009295cf522f899b01a408fc
- audit-0194de02779733d753e1c3c5
- audit-022870669bcf99544958a563
- audit-024013843f665bdc3727e427
- audit-02ec285eff95564fa11371c9
- audit-03374abf658570e9ac35190a
- audit-0394392d9ebf1acd2d7b47c7
- audit-04c54e13cd6f2c93dcf4b5ff
- audit-04ff7b22ee29a834a04ddaaf
- audit-053045b89622f2b877cae750
- audit-056f5923adfec623bb481c14
- audit-064147585dd4a247a735c924
- audit-0686053400c4e57f4905e415
- audit-0736bedf0d9d99be901156f0
- audit-0746a6f3f16ba58a4423a58f
- audit-087cc13bf2141b825eee6a94
- audit-08ac68c22527f4e0fdc45b08
- audit-08bcb1cecd7d8709752d5979
- audit-08d7580e12c3ac42047f21fd
- audit-0902e02055418884afd4580c
- audit-0976c46bfca004a198d583f8
- audit-09f71b1d37e4b961c697c86f
- audit-0a3c94fda1363908cfe193e0
- audit-0b75183713fb23630b5ed307
- audit-0bac0629fef2c8d3c6513c18
- audit-0c9f8051ec5995addc8c1814
- audit-0d0f098847c7de4cb14ceca7
- audit-0d31f0fa08363fcead099fcb
- audit-0e3e569edde900e91fc871fa
- audit-0f8d32f6cbe6a19cfc150bbf
- audit-1031b417e87c63b57a4943dc
- audit-117e7d87562f6d3a6dda53ea
- audit-11af3023911d85ad3b09b978
- audit-11f56bf9c94d5b5192c9f405
- audit-12a08817b73c0f9198887f1b
- audit-131ecf2bd894ea619e324c71
- audit-1329a473a272d49e068ebc08
- audit-136ce9151c2398a3e345df90
- audit-13f32e5d03c16cba7366230e
- audit-14c3e02b006eec5561410c41
- audit-14eb8a1b6f3e92eded6de89e
- audit-15257ca18b80e2d4d3373f04
- audit-15d0b264279c9ddf604a9b1a
- audit-166bddc2a7c0c0c9e12d9c8a
- audit-16dab36fecfc6f2359c981ea
- audit-1788494f4b12bf06694d89ed
- audit-17a32a9a8833c3e6bc275214
- audit-17c0e03068746cb386e69bc0
- audit-17d317aedd48df8ae05a2b94
- audit-18241c771e9e97dd60bc5a46
- audit-182ffd28a585715a907f0c7a
- audit-186013b2f59a3f227ee5af50
- audit-19367cea561c9de63c62115b
- audit-19c14ba97eca3b8ce29d069e
- audit-1a35e13eac5a68c449e409e2
- audit-1a36b84ef8073ee9de9f55fc
- audit-1ad9c8399a391bdafb276195
- audit-1ae0586e563d2a5a67e3f173
- audit-1b58d98dcccaea9cf4002fa5
- audit-1b87bfcff25a7b2dc400e025
- audit-1b8f695f61c1e236c8b2d722
- audit-1bd02556a253fdd09e0d93dd
- audit-1c0750fc6d9bb01bd8cd4bce
- audit-1c5b362210d76cbf04c8e3c5
- audit-1cb2cb23b507ce3de85ccc60
- audit-1ce1337dd1648078ef38c14d
- audit-1d0b0cd68684b053c8aea2e0
- audit-1d1158a1b1f7c2a2dd1e8e99
- audit-1d38119c8d21ed43ad1db9b7
- audit-1d8d0c254c09d5fffd3a8faa
- audit-1dfbf8c07821e5e90f7349ad
- audit-1e1d5b01a8f3e8445631b478
- audit-1eb8dc99b92ff02194505d63
- audit-1efe0595e50ef74b45e0a67e
- audit-1f563b7228a53077a7e67a9b
- audit-1f58b545d2ff6a01917fcc3b
- audit-1ff33a1d65c0b68b44e2b7d5
- audit-20324998d1eff0024b7f224e
- audit-20558d9e3a3e2cd95d71e603
- audit-214dc923c0cb6256ec4a6b4c
- audit-21b84d44cc054b32e5b5b664
- audit-221e5c5d69c7ffa948ba1c97
- audit-22c283c155bd1579161e2243
- audit-22dc750275378c1836da2d74
- audit-23434bff31dafcd7bab4e601
- audit-23449ad5d9d5d7d9e9816d45
- audit-238ca3d5f548645965f60ded
- audit-239b02a6b5caf1307fe7035a
- audit-23da19770b7212cd4f3588cf
- audit-23eb225fc829f53a3a1286dd
- audit-23f0382eb0a6993d9ecfd9a5
- audit-246c94da80fa14f8bc2b2019
- audit-249f5b5349c4cf6e956febf6
- audit-25c57923728552c3ef04e9db
- audit-26200b78c28ea50f70dc23c0
- audit-26605843e215425bd296fa90
- audit-273239a8253fd9b1e5d6e801
- audit-27a091ba95f515d130bdcb74
- audit-28325d3fddbcdca0e96b9c20
- audit-28762ff57b46f5a1c4833b44
- audit-28dbe2b16c69d98c265e9971
- audit-28ea10a6d666a6f11bc610b0
- audit-2945c5f5100f18274ec9c36c
- audit-29a5e7130b26c43135357bf7
- audit-29facfd314cc85f073767263
- audit-2a9b04b7e51e9def117e7aba
- audit-2af5abcb7edb05010722e048
- audit-2b23da9d90be9704eb1253c8
- audit-2b5c1c4ee81b3122ada50507
- audit-2b926f0b5ce37af9f99879fb
- audit-2be29a80ace9f36210b6321f
- audit-2beb5e9a7b55dbe347fb5b62
- audit-2c0f7ccb519264ec3f567013
- audit-2cc623fb445c2ea35626e34e
- audit-2cfe4bb8c2cd1068287bb89b
- audit-2d781d7d59872be8def74a47
- audit-2daf7630aabbcf6488341102
- audit-2de93e073663c89e69ea64de
- audit-2dfc2e184e85f36db9f9949d
- audit-2ebde4dc412b9beba09c739f
- audit-2ed8bd509199f2ed2db9777f
- audit-2f746ceaf957b8d9353cca3c
- audit-3020a7098dba616f467c4b44
- audit-3072a33a7b600f8d6c8dc86a
- audit-30781898ddf0435c2c4fcea8
- audit-30875db7b7f6cbc272afc0b8
- audit-30ef9cac3dd2a6b8c36a858f
- audit-31a1179db29ea95c429ca7bd
- audit-32ec67eaa59216a711fe981b
- audit-333d1d092d465b7bc839a92c
- audit-33497aedb68f64cd01063aa2
- audit-3351745575fad4606ce5bf81
- audit-33b7945a6a7faa89dca2ce57
- audit-34163e14ad9e400eb6e80445
- audit-34e0faab7e44312170df9653
- audit-34e9a3e9b01667c403ae4027
- audit-34ef34f784613ce045457626
- audit-3509114e6159d4b4d2051069
- audit-355c15c5eb0d6b6986b9aee0
- audit-35a3dc755689f113b870d13f
- audit-35b959c5616f2c22378f8356
- audit-35fc13c049a240418b129820
- audit-36022e8a9aba71381ae325d5
- audit-36b1199030046dad43d34956
- audit-36c8be1ceef76e86002e0c31
- audit-36f57d9ba85cee5721563319
- audit-3761f3e1759f02416f903851
- audit-37971e81d646921b806b61e4
- audit-3811c3d4b8f458575785b4ab
- audit-3825f885ddae10f5abd32355
- audit-3859a11d40d93522a849f75b
- audit-388a37a0e60fde5cfe7d1818
- audit-396c4251c1ca5c8740db82f4
- audit-39796cd78ea92faec479c306
- audit-398834ea6fed6412d004198a
- audit-3a67982502114f4fee6b9239
- audit-3abcf24b03cf3f2593fa34c3
- audit-3ace4c3b2bac3df1ba0811ce
- audit-3ad1303d7cb4b5ec55be7416
- audit-3afb3272300bd4d0f9eb8fef
- audit-3b02a2168273b77a4712d353
- audit-3b5139a3edf96612469a0499
- audit-3b7da4399c953f2e1324bebe
- audit-3bf50330f52ab2ee52a00167
- audit-3c8346866ba6675bfbd62653
- audit-3c98b06a133f12458fabe140
- audit-3c9e944d6071ec3630c42b75
- audit-3cb541b8db40d083d20019d4
- audit-3d2c7eaf77f5000600e63988
- audit-3e95e0e427213bc8e2072876
- audit-3eb902888cf286a5c0877f76
- audit-3edec3f51ada2d06724ba1a4
- audit-40a91276c276f72449104bcc
- audit-40df438efe23a226f771b360
- audit-41600ff2bc7a8cac0fc9cf47
- audit-423d3f191bf9db61e3a501e3
- audit-42bd9ceee1817e83de8177b6
- audit-440f73a75d06a2c331e5f975
- audit-44e3429999e13d2dbcf14afb
- audit-45775a91e4ef9888250419fa
- audit-459bc1192979a0b5bdd58174
- audit-45c938f91abdaeaa64104c9a
- audit-45e5f90fc7973fa1c6201a6c
- audit-4611e325c9725e199841fb01
- audit-471e77bf6aac61e13c31432a
- audit-4768c8c88d706cbde8a7dfba
- audit-48108c6788fb8bd1f9913646
- audit-481b0119c7553ea0fb70ab99
- audit-49030b3be2601499eff69eba
- audit-4955df657f81e75188165a33
- audit-49ccc73557d9719bb611a353
- audit-49e209ece1f287c415fc3cda
- audit-49ff35ecbf2173f11c64fe51
- audit-4a013c5a342041761b41af96
- audit-4a03c0ffad803ebf08da3b9e
- audit-4a8d10b20cfe3d6eab72e0fb
- audit-4ab827afbefe15870c401055
- audit-4bbcc56b3b28ef05aa25ac57
- audit-4be627c4492dfdb1748f155b
- audit-4bfcfbeaed749f0045d98c39
- audit-4c0621ee2fdb90194dce52ef
- audit-4c4375221352c0a98f3471eb
- audit-4c459d03c64b0f9acc352d4f
- audit-4c7919067c6614e6e0c9c69d
- audit-4d416e08b1365dde266653b9
- audit-4d45eed4e65a6d15c2fb487e
- audit-4d7f17524292e525f7827675
- audit-4ec2eb9689fb675546648ef2
- audit-4f0a80c5399e5e6317a82163
- audit-5000bd0f88425685db4c52f5
- audit-50532bf0b98c92b46271a76f
- audit-5067c5afde3e32163c91d3a3
- audit-50c8d08fa608c5449d05ece5
- audit-50d0af60a799ffac24a60c66
- audit-50e14fe28ca178906e35cb3f
- audit-5103359ada50478e9fde7d07
- audit-5166780869727dece5c9c115
- audit-516e84e2ab19c334984d3ccb
- audit-527e3ef23f165903926db6d8
- audit-52c6889686532dd3d152db72
- audit-52d367d99c59ec01a4793a12
- audit-53961e5a2d28d0145a607c04
- audit-53ad38a5ef7896af5a5a8ae0
- audit-53c833df8803836145ec6c08
- audit-544f832bb742d9c332886c23
- audit-5460ad2e73bf5d2355a8d9e7
- audit-550dac0c6cb469be58c545d4
- audit-5523262764228bcf7f6aca21
- audit-55459678f56fa2d4886313ec
- audit-555a38474c6021e6d11aeaed
- audit-5574e57e15344befd3ad48d4
- audit-55c7feca5113ba1e907d2259
- audit-55f5273c5c41ae154f8db016
- audit-560143c249f47212a7a50c92
- audit-5622d38a7b997dee4b5a1a26
- audit-566ea80bd7110cbdace9d682
- audit-5809c968456fc561542a650c
- audit-5892d7cd9ce401fe392f43c0
- audit-58b7ffc584ba703157a95b0f
- audit-58c3511b27b72a9f23b07b80
- audit-58e7f7d7c9550f85e192e904
- audit-591f8f810d39849e8f18c795
- audit-593f20f519c53bf73a2198a0
- audit-5970bc03fab2baa35a941c9c
- audit-59da96dcc5050aa129c545e2
- audit-5b074aa7ff579496e2e40027
- audit-5b118a5431c556968f16e703
- audit-5c420961e3e5ee7791d90b69
- audit-5c50040d3b1fa927b3ab2732
- audit-5cecdd216266770d1ec6505f
- audit-5db4b78ca128b3ac8aa065c8
- audit-5de79de3a9e55f158fe4a609
- audit-5e4bb3f1261821bdafc7a08f
- audit-5f204d285aaa4ddb37f910ab
- audit-5fc1e4ad4e2e4eb3c03f4198
- audit-6015b743d5413add94b3675a
- audit-60f379d2d6fe17c7dc81551b
- audit-61c964f6475adeb5d1b1725b
- audit-61db965d073a21c14cfc61bd
- audit-622b8fc4a5dd6d281fae79c6
- audit-62759786af0db703af677ba1
- audit-63447ef18679fc69918b5eab
- audit-6371fe7461d8ee443e40075d
- audit-63c8b8af413b250d80d4a33c
- audit-63d87269c5674045b961b46d
- audit-63f87840b41801e2693f88ab
- audit-645faa994ec6a02197a7733d
- audit-647c420e8d67cbcb0f5f02ef
- audit-64902bbd12bfacdd9f4fb11a
- audit-64e2e118441597f3ef2b033f
- audit-6553d8d87226878e7a9c5567
- audit-6570b4a510392991f91f4fcd
- audit-65d3a9cdb6b125393ab17ef8
- audit-661b5062f340eac169ba2a9e
- audit-66297a7a86a40d1110203bec
- audit-665d98c44f54a306ee2b8035
- audit-66c3a8d546d48a143a374bf2
- audit-671cfb049f0a6fe349a5723a
- audit-67213e8592aecc84b404b824
- audit-6729f45123dd397b340705af
- audit-67422417265f9fb5d65dd229
- audit-67460ad06997443fc1aa7aab
- audit-675b6a158fe175256a174755
- audit-67ce8ad05116f429c704d4ea
- audit-6811658dd54e113c86e0fe45
- audit-68341ec4248fa4025bada71a
- audit-6882dc89a3676d79f31079f9
- audit-69b1c8044ef0df3ecd4d3ca1
- audit-69c10026e0262281f530c277
- audit-69d719c9675a7b627ffcc175
- audit-69dd1f823cd2e20dac3e6d74
- audit-6b10a74b633d925081ba7270
- audit-6c6905850a89775f95f78edb
- audit-6cb4194eb0ea3d3eec7d0892
- audit-6d619b0f98b590e5e45b87ae
- audit-6d91bf22124c732a934bb6b7
- audit-6db61fd344c330631e922003
- audit-6e18be2355da2bf69d8a3746
- audit-6ee003215f6a304c3b44bc8e
- audit-6f3714a4344551f2a2651c17
- audit-6f591972654512e5a2e25910
- audit-6fed3a9a4cecba456d5e456c
- audit-6ff581a19000966322b209a2
- audit-706cb87b86a85ca9005f9006
- audit-70985f0b9445cffd933db247
- audit-70d99c3c54e5d35d40915e02
- audit-70f9b8d4c87504b836e25275
- audit-71a41511303b8f5268be222d
- audit-71d8aa40d324370e84541e66
- audit-71d99ace493f94724d72f5ca
- audit-7254a50abcedd23054484ba5
- audit-72c23bc3ed7bd67371c7bc12
- audit-72e8f1ae362001523826a45b
- audit-7321c0e1ad6de6a3e51096ce
- audit-74a2ae00998aff33dbe42420
- audit-74b9543fde149f93e4d4483a
- audit-751869c87de23a8eb2d755b5
- audit-752bed2eb74af8228bf952e5
- audit-7535ca1a608d20b19c511b8a
- audit-753f4ec86ddf98155e216f82
- audit-7574ecd9e32542b12217ae71
- audit-75f582d33bc74685c6b4bd4d
- audit-769a5cfee7c732f2fd940e8f
- audit-772d97e22c74ad400ee2caed
- audit-7798a9d4c8ae6fe1a0ce8620
- audit-77b5323c6cfb3bc1ef5e7da3
- audit-7868ee5ad60ed24acc95ae45
- audit-78b6cc4e54a4957ac3c98145
- audit-792cb7cc7c7d56da2f9c0e10
- audit-7940a0f7fe29ddd408918171
- audit-795456eb0016dfc2bb1aa018
- audit-7983b66ad37d949072da36ed
- audit-7a9132e01e992cebdbb12e5b
- audit-7bc5dd090ca007e2424fc07c
- audit-7bd1b3ebbf5920847d5b5596
- audit-7c026a203ff1645557db828a
- audit-7c4bfe303c1e1376a633cb60
- audit-7c74b4cfba9bd536f0c0358f
- audit-7d0c52c1c771bd8cb7201818
- audit-7d51cf5435c28cccd60f95d5
- audit-7dc856b3a0723704e971507d
- audit-7e11eda7822951b370eb9e8e
- audit-7e1c6e0b6258d1acd40605ed
- audit-7e69b92c747edafe0ada7a2c
- audit-7f215d586d3bdac3b82baacd
- audit-7f2fb152a4b587a85f43a398
- audit-7f410b33a4e61ccde4ba5a8c
- audit-807be735ae40e4e0f249c702
- audit-80ed8d896e182b472d7ec470
- audit-8129a2e931cb699905649b03
- audit-825e01497b04a4dc02a12637
- audit-82e4ec77cb88d4fe8009a963
- audit-83bfb334aedc5ce7e4de0edb
- audit-8474bb6cad58a1286e9a5518
- audit-8516b2577bb3709c1b93f832
- audit-8522a43b81f2d09608aa84e0
- audit-857aae7a0278dda6de6152ed
- audit-8595a921c784c05db35d7881
- audit-862b0204a7b82f9b8811917b
- audit-866dfbd78c677c45de55054f
- audit-86ae3f3c8179984cce3d3c2a
- audit-872e4df50b84f0e64c6aa89d
- audit-873069cc200cecaa65b23637
- audit-876ef16263c7a0b6efa84f5e
- audit-87968ef97c1d0fffe719d87d
- audit-87b42d6fd360818ce6ad242b
- audit-87da024d369c2d56ba55d90e
- audit-87ff4ea95603ab83ec5d8fe5
- audit-8886eaf61574cfb8ffc57a2c
- audit-891298fe248b7ce2d0d09a9a
- audit-8924a51982aef34f013a5d9f
- audit-893920a2730db18858865527
- audit-89c50276a0b296b3557c96ff
- audit-89d377dc59555519a8cdcbeb
- audit-89e4f1f495f34d1299800053
- audit-8a99453c5c0378946cb32d03
- audit-8addcf8ee09597f03e7d0aa1
- audit-8b519a87f2e144eac0cea56c
- audit-8b5c6cfe56096abb261292ab
- audit-8b736f7687f2839480c02b71
- audit-8d11283c6ab105a662ff7c0b
- audit-8dd7adf773578ef9a8dd3d0d
- audit-8e1996310b618870f8c1cff4
- audit-8eaed73d58fafd05a578fb2d
- audit-8ebdddb356d4dd220f494001
- audit-8ed7200d8d6f75a59344376e
- audit-8ee7e4e3d9a4d9247a21e083
- audit-8ef10afeda182ece0cbdad40
- audit-8f2e85bcc82753bcdc61ea8b
- audit-8f9ff1a8c748c9842c2204fb
- audit-910f3cb6b01a46da6eb2815e
- audit-911dcd0b99b92a9d724863dc
- audit-91ce852b34e7233694fdf45d
- audit-92d2f030615c1b9b7265dc20
- audit-9353a0c45b1a6a9531e229a2
- audit-9384b52c2bc0ff460e2b14f6
- audit-9403f6f8fd9afde371358791
- audit-940c46e09626862bf855af5f
- audit-943d8c9a84f448046d43e72d
- audit-9502a37f66c775e3cacfa74c
- audit-9561c5019c4c87ad6e1073c1
- audit-95cbb0ce79ee732f6df21abf
- audit-96411351f4d7e98cf1812c6b
- audit-96b050f0a56c83cfb628f4ea
- audit-96bf39a386fe4476fa6c5d1a
- audit-9728a1232f22f51534c2958d
- audit-9739eb77c2eaeb952cc27826
- audit-97b679715cfe6e5e3b3feb55
- audit-97dfff1fdac39b75d30d6744
- audit-980e9b9efd9dc870fdebc3d9
- audit-99a0823956a8f41d0130bee7
- audit-99cc29126c5d17338dee6f2e
- audit-9b09d25682811c14f0f754bb
- audit-9b7d879ed8f2fd494917f519
- audit-9c04bc82dfcf8a6b5ee95dbe
- audit-9caa6bbd775d23a226276549
- audit-9d4a85fb8c2cc8b5a1009957
- audit-9d725dc2fccae2fbddf81d4c
- audit-9ddebb6d73a8c89bad0f8aa7
- audit-9e1146a0c655d98ec5535212
- audit-9eb66380f2a93b98a4a640f3
- audit-9ee662be4f173c07deb94e43
- audit-9f09744bbaa2716faec27795
- audit-9f1bc045c70878d4cfa535aa
- audit-9f4e8032d12a111e59a1dd65
- audit-a01125a81d1331dc9ee19808
- audit-a077917008b82c00072c6e56
- audit-a0919241688cbb20980dabfd
- audit-a0c1d39461e0bbc0cb4e8083
- audit-a20022b585fa04409ec3dc9b
- audit-a2efbea4713e88f7af0212e6
- audit-a34dd049b8fb371311fef592
- audit-a35a42d8a464909c23681a48
- audit-a4ca3cdd06efbf224e661f78
- audit-a4df0ce2de4204cb66a9632d
- audit-a51bcb7ef59ef0871205a379
- audit-a5233ffbbb686c852ad4dcaf
- audit-a5286aed8487fc74acc81ce1
- audit-a57548b26fe8f208cf4dfe5a
- audit-a5a03a78f4fc15c579a7c8af
- audit-a695dc0a69279094e0986d39
- audit-a6d927eeb5a75beb4207fcd4
- audit-a733c26bce35f8c871d52444
- audit-a73535ef549c3354cb491d1d
- audit-a78f5da15740b64d11e7ed07
- audit-a7b18dc28846287a875d58fa
- audit-a7caf6111b770d338a090e01
- audit-a7ebe95960d026d6e6c36d71
- audit-a968fff37a020125bee3e716
- audit-a97052653617c3be1c101afa
- audit-a9771686de8ef15627b50c96
- audit-a9bb0f3ee793b372b2916af2
- audit-a9f9ff5608f25b4075921c7a
- audit-aa026e3a8c39504656a20252
- audit-aa0ffcc3c3e1f4244f6ba755
- audit-aacc21ee6380c3d38078d3ee
- audit-aaf2521bdff68c4c6c0d4a15
- audit-ab0b1690abfc5f8a250be7c9
- audit-ab2caa8f99d3738429b5529f
- audit-ab432e4ce4ddb7c125a9096d
- audit-ab903e5e341eb1b114c8ad28
- audit-ac0930da6a1e351109b27d44
- audit-ac593182019bb00c740bb3cd
- audit-ac7ba4822fc9d8f149b8d27f
- audit-ac9d03171f81c36055722e6b
- audit-ad420c3960623627d95e04cb
- audit-ad527a6563d5b888cb901cbd
- audit-af93b4520815aacac7356d39
- audit-af9eb3561c21291a60de20ec
- audit-afb42980506ec79262655ec0
- audit-b017dec61fcd4a26bd2e5d8c
- audit-b03c726076201b3026c62141
- audit-b063d06c83506f52d49c5f62
- audit-b0c7fac29e4295ffea24bbb8
- audit-b1686b5244edb05e225e9676
- audit-b173b3115b19c5c46ed03834
- audit-b189c37a2cfe0fcad1dd73d3
- audit-b1ef86bb773dcf402fa54dce
- audit-b2a6d43a1cc54fe4e0442784
- audit-b2f5eaf086576bacb77702ba
- audit-b339b176b9f47cddbc11d376
- audit-b33c8947c9b05ee40dbe2239
- audit-b371b973512047b58c3e59ab
- audit-b3e44cbae9b94b0eee27656a
- audit-b424cef4c8093cce6156e615
- audit-b4c65972cf6e4e7d34cdb046
- audit-b50d269538fbf1b066cad3c8
- audit-b51c29d6df448ec9c9d415f5
- audit-b5bafbb7e8c9237ac9b066ea
- audit-b60a65101827d4222cb8b6db
- audit-b6508f46d20cd42c8b527935
- audit-b6ed6601d2048679739ee372
- audit-b71c6147ae80a855b876c589
- audit-b73deedb06bc2d259953508f
- audit-b7416c440b87b8c6bf7d1cac
- audit-b81a6c5e662c855a6908ef63
- audit-b8c5e2fd08d10b9b0d92fa49
- audit-b8eb81f48995e67c6479d6a3
- audit-b8eeca93dc482eab99afb2e4
- audit-b924cd173661305a0ba03b88
- audit-b9b93f462755d435790b8679
- audit-b9f6ce44cbac8ff6b48a0cce
- audit-ba973d963db5df127b2a4458
- audit-baaf0cdf4fbc303396b9d52d
- audit-bacfe55ecdc52903fa1dcc1d
- audit-bb5f958051d276b4ec8ce9dc
- audit-bb92711f79cebd6093d968ab
- audit-bba7454e3731bf5e59b4b7d8
- audit-bbebfb33d0d45ef7eefab417
- audit-bcb5a516456cabaee70d067f
- audit-bcc4081bc6eb428d1027cb77
- audit-bdf118b1264116a196b96989
- audit-be24a8e38341f25f5eb34816
- audit-be5328d40fcf17cd53ba5714
- audit-be8aabadc40c79cfc32c72b9
- audit-beea2913a5e8bde743b43132
- audit-bf0b0731d7d6dee0f3ddf80a
- audit-bf87913f34cb5ec583e3ec34
- audit-bf9defbd57e7487389a071b5
- audit-bff4490b7c35eca40c43ef74
- audit-c00364ee172db1b30db3e750
- audit-c14bc24dee5b214d79b70b24
- audit-c1c2fb2479b68fa20bb30db6
- audit-c28ffd3052734c21db525c65
- audit-c2b917003ef4c30f3e21bbfb
- audit-c2c4ca1700e89b56d8397fbf
- audit-c2e6d4054261761e83079c68
- audit-c3eefcc3868430a955269161
- audit-c3f78fc5e5c43eb8b3a40664
- audit-c435e637a451eee8b4c9519b
- audit-c451156daeb161bd4c26b60b
- audit-c6473ec63371067c33d6b7bb
- audit-c8634028bef4a6a6c311920f
- audit-c8b194fa4413c562e31f05e7
- audit-c8f2e7169d051f77c520a4ca
- audit-c9663199d0d242647e141519
- audit-c9b35a89147c782fc3ec2fdb
- audit-c9dbb03cc7af98c613c23ca4
- audit-c9e51e971ef3ca96f48dfb1c
- audit-ca4c0523c0a1788c55858d87
- audit-cb4dee57175e35c1bddf1786
- audit-cb5394567007dd95abcf88df
- audit-cbb48e32ad4134d229fc6df6
- audit-cbb550201bd33990364a749f
- audit-cbe8e381f142853a98f6126a
- audit-cc044373673b85c89b3a5b84
- audit-cc8b795ec6edbb43f12eb3a4
- audit-cd175c5d2c15cb645fa7b020
- audit-cd355f26f63abb1b434d035e
- audit-cd4e8e061a37a799098a473d
- audit-cdce16cc73f601b410902567
- audit-ce1d489cfd659aa3e0cdf593
- audit-ce5bf0488824add21ec85ea1
- audit-ce72e476f6a5706590cfdceb
- audit-cecc3dc954f750ba46c9a2c3
- audit-cedac25e52a0fbe8eaef1f1b
- audit-cef3f045bf2e1dfb56058563
- audit-cf72792f77aadbca9e70dd60
- audit-d02a3c069fbac0652c511296
- audit-d03f1d51c65edd4400dd333a
- audit-d080a510232c976d4325c52b
- audit-d18c1f8018f0d367b4d107d3
- audit-d1b64aa6ba0671a49bfc3093
- audit-d1e3023341fc23c5543a665a
- audit-d23ea8fbd4536c741901bccd
- audit-d25868feceff55510c8c12b3
- audit-d30088b8da056864802487f7
- audit-d3ab75268a01d8102ac5b3f3
- audit-d414089d1a80c8cee2c0822f
- audit-d5078ead72ec8612149c901b
- audit-d5410e59273cdeb9e89be865
- audit-d5a6ccb2e0b7ac85e642b8c2
- audit-d5d91b82f8c1211a4d08eb03
- audit-d5f05d31d832f0327b801906
- audit-d66d5a07b904829c2c75dfea
- audit-d671c25482634c5d37fc01a9
- audit-d73bc3321bf45e6e480077f9
- audit-d82081937bb9356b35dccb2a
- audit-d89609aa7d47dfda94261cd6
- audit-d8d23ed2c3752374359b2e1c
- audit-d8d5661e1d80efaacf0236be
- audit-d91c5f420b36624b8594d07d
- audit-d9579e04230a59f9218185ec
- audit-d991d8cb42074f83927898a2
- audit-d9d2adeba39b5390da6a523f
- audit-da6fc434e2832d585d13f92a
- audit-dae044be7feeeb9dee32119a
- audit-dafd849736eb3221530d1934
- audit-db5d29c1a7da956bed43d0ee
- audit-dbb958f2184c74116e5deb15
- audit-dbc8fc57f5a959794b7d9f13
- audit-dbd273153003c4d130dc723a
- audit-dc46d0a52993ff9a347172c7
- audit-dc7c1ce2fecd3ccde9d47400
- audit-dc860e6b0ff8b77ae2eb4d8e
- audit-dcfd2c829f47292d91572350
- audit-dd9fc70352ffecb5ad7786af
- audit-ddac1058ef2d3100bdea9250
- audit-de224e3a33356d1fb5bd91a9
- audit-de400d09407f1beacb8b72d3
- audit-de4490ac04bf330b27955d2b
- audit-de61ba4251ae71829b52f91b
- audit-dec2a53478241ad22615979d
- audit-df09745693f2cf0a6cfcb0d9
- audit-df673a3aab7237bf10e2afa5
- audit-dfd1fc7bd87bd2cc2cc89660
- audit-dfd391ee4cf76cdc13688a71
- audit-dff8a668a98d0fc40cfce057
- audit-e0047623f3519ae411b2a112
- audit-e01a9a77569a1b7f92793cea
- audit-e05206f48be2776f1d538b2e
- audit-e11d133458e4204f200c2f04
- audit-e1d3b09de2eb9200b739be27
- audit-e1d4bfddf8782fda24506584
- audit-e25a4a6e428b166b5f6ec1ac
- audit-e33a16c26383710a462abc10
- audit-e41910f7d0742678cdb8544e
- audit-e4191e2c598cec7245842397
- audit-e4880660854a7ce7370d3a15
- audit-e5c4722c895ff88336381d2e
- audit-e5ea042629e537885966be02
- audit-e64a8881abeaec916a0c35b8
- audit-e6685ec189460e76ca55e836
- audit-e6b8b1039ea6888f922931e9
- audit-e6cca776cbc1837d735742a0
- audit-e6d899aa478a88448b8d531f
- audit-e7da83c3af92c4a035ddb2ae
- audit-e817f36fd0731fd2640ba4ce
- audit-e8a5c7bff24819492c325072
- audit-e93e2acefd5fb8f5240821a7
- audit-ea44bc37e7e2d7e9b53fe206
- audit-eac0cb54f80b44042517b129
- audit-eaedc70b9aa0c8757716c90f
- audit-eb225e1e1ecaf947c182a40d
- audit-eb63f757eed77ba7f50fd2ee
- audit-eb649757e1f866a4d98a0f69
- audit-ec32dd278c80f604b5c7537a
- audit-ec89dc492eef71b83d629ead
- audit-ecc6f83a9842d28dc2223192
- audit-ed515016b4084994da47d894
- audit-ed5a8471669ff1813cfdc41d
- audit-ed629010e389a7f5a9234ed5
- audit-edbd1947562c97ce50f68daa
- audit-edc00f02d705e8b3ebe51a38
- audit-ee1f30f1dc5f340226980e23
- audit-ee256e61354ed3dbaa2493af
- audit-ee72686ed565c9b00be832df
- audit-eec2b38d8a94f4897318b92a
- audit-efde53a4b7c15eccfd03e463
- audit-f009ae757694ace48e0ce1c1
- audit-f0dff54171a976b9f020de0d
- audit-f0f7f22ab99e9f1f4aef1273
- audit-f127b02a07be934c6e5d5afd
- audit-f1488dfc0aaed2f0a8822574
- audit-f2c14d5807926d97d76692fc
- audit-f2f4fd4c5d23bb1681be79eb
- audit-f3176f2a081ed6e811cd4f1a
- audit-f39729e570892215410126a1
- audit-f481d96f8ec5573d4ecd0e24
- audit-f4955b8e528cfe4713140a7e
- audit-f4a421052a854d34bb743b4b
- audit-f4ffadd3f662b6c9912137c4
- audit-f58bd99ab16041ed879dcd7f
- audit-f65af01ef92c845681a4a2a7
- audit-f693015c8a5e6034d01793b0
- audit-f6d51657ca21910eb6543910
- audit-f820c673e2291b267d58ef55
- audit-f8556e4a031185075d198e79
- audit-f8ad1c05159c54abf917728e
- audit-f91ce6f3b594c83bf5bb3718
- audit-f926006563ed930107c04e9f
- audit-f963b3dc2743bac8c7611a2a
- audit-f98350f5b692229fd4e4c774
- audit-f9faf030b1f60393837119f3
- audit-fab4839a82fe857b6e183d72
- audit-fad62133ba595dca81ec866a
- audit-fb16dbbf22451644960a0f5f
- audit-fb4d7906c079ca63bd08aea4
- audit-fb7c5ad55c286db65110047d
- audit-fc8693df82128459e7720cb0
- audit-fd37c4d9eeeda25344ce1a32
- audit-fda6c6720496565b8392b9b2
- audit-fdd24f254233c07c8820e274
- audit-fe19dc5d7abcace3790f2b12
- audit-fe8ab80212191572b3c44c93
- audit-fee4d6e33eb226552e92d423
- audit-fef6bb6e68254194cb735cfd
- audit-ff23b09fc950ba21e655fd40
- audit-ff30a1a61835752119dd7eeb
- audit-ff5e172ec52c11dc3796c54d
- audit-ffbf42f508ab844652028a70
- audit-fff10fce268d807817785d19

## Deterministic structural findings

| ID | Entity | Rule | Finding | Triage |
|---|---|---|---|---|

## Human content review (not approval)

| ID | Entity | Rule | Finding | Triage |
|---|---|---|---|---|
| audit-3c9e944d6071ec3630c42b75 | passages:auto_366f70fa | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-49e209ece1f287c415fc3cda | passages:auto_51732c82 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-59da96dcc5050aa129c545e2 | passages:auto_62abb41c | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-cbb48e32ad4134d229fc6df6 | passages:auto_8173a36f | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-ee256e61354ed3dbaa2493af | passages:auto_8afe3a8d | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-63f87840b41801e2693f88ab | passages:auto_9ac36e62 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-f39729e570892215410126a1 | passages:auto_f76e487c | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-d1e3023341fc23c5543a665a | passages:auto_f81c35a0 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-cd355f26f63abb1b434d035e | passages:bank_2018_1_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-0c9f8051ec5995addc8c1814 | passages:bank_2018_1_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-f963b3dc2743bac8c7611a2a | passages:bank_2018_1_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-aacc21ee6380c3d38078d3ee | passages:bank_2018_1_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-eb63f757eed77ba7f50fd2ee | passages:bank_2018_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-ff5e172ec52c11dc3796c54d | passages:bank_2018_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-c3eefcc3868430a955269161 | passages:bank_2018_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-fe19dc5d7abcace3790f2b12 | passages:bank_2018_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-1d38119c8d21ed43ad1db9b7 | passages:bank_2019_1_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-b6508f46d20cd42c8b527935 | passages:bank_2019_1_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-c451156daeb161bd4c26b60b | passages:bank_2019_1_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-4611e325c9725e199841fb01 | passages:bank_2019_1_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-671cfb049f0a6fe349a5723a | passages:bank_2019_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-396c4251c1ca5c8740db82f4 | passages:bank_2019_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-dbc8fc57f5a959794b7d9f13 | passages:bank_2019_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-de61ba4251ae71829b52f91b | passages:bank_2019_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-64902bbd12bfacdd9f4fb11a | passages:bank_2020_1_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-645faa994ec6a02197a7733d | passages:bank_2020_1_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-ce72e476f6a5706590cfdceb | passages:bank_2020_1_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-6cb4194eb0ea3d3eec7d0892 | passages:bank_2020_1_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-eaedc70b9aa0c8757716c90f | passages:bank_2020_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-80ed8d896e182b472d7ec470 | passages:bank_2020_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-a35a42d8a464909c23681a48 | passages:bank_2020_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-53961e5a2d28d0145a607c04 | passages:bank_2020_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-18241c771e9e97dd60bc5a46 | passages:bank_2021_1_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-6570b4a510392991f91f4fcd | passages:bank_2021_1_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-e5ea042629e537885966be02 | passages:bank_2021_1_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-f8ad1c05159c54abf917728e | passages:bank_2021_1_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-ddac1058ef2d3100bdea9250 | passages:bank_2021_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-a968fff37a020125bee3e716 | passages:bank_2021_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-5f204d285aaa4ddb37f910ab | passages:bank_2021_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-aa0ffcc3c3e1f4244f6ba755 | passages:bank_2021_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-dbb958f2184c74116e5deb15 | passages:bank_2022_1_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-5c420961e3e5ee7791d90b69 | passages:bank_2022_1_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-22dc750275378c1836da2d74 | passages:bank_2022_1_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-baaf0cdf4fbc303396b9d52d | passages:bank_2022_1_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-675b6a158fe175256a174755 | passages:bank_2022_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-55c7feca5113ba1e907d2259 | passages:bank_2022_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-edbd1947562c97ce50f68daa | passages:bank_2022_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-de224e3a33356d1fb5bd91a9 | passages:bank_2022_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-166bddc2a7c0c0c9e12d9c8a | passages:bank_2023_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-d9579e04230a59f9218185ec | passages:bank_2023_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-d8d23ed2c3752374359b2e1c | passages:bank_2023_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-86ae3f3c8179984cce3d3c2a | passages:bank_2023_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-7321c0e1ad6de6a3e51096ce | passages:bank_2024_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-96411351f4d7e98cf1812c6b | passages:bank_2024_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-a7caf6111b770d338a090e01 | passages:bank_2024_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-0e3e569edde900e91fc871fa | passages:bank_2024_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-131ecf2bd894ea619e324c71 | passages:bank_2025_1_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-cc8b795ec6edbb43f12eb3a4 | passages:bank_2025_1_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-9ee662be4f173c07deb94e43 | passages:bank_2025_1_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-ee1f30f1dc5f340226980e23 | passages:bank_2025_1_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-4768c8c88d706cbde8a7dfba | passages:bank_2025_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-bf87913f34cb5ec583e3ec34 | passages:bank_2025_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-1d0b0cd68684b053c8aea2e0 | passages:bank_2025_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-e93e2acefd5fb8f5240821a7 | passages:bank_2025_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-e1d3b09de2eb9200b739be27 | passages:bank_2026_1_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-eec2b38d8a94f4897318b92a | passages:bank_2026_1_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-1a36b84ef8073ee9de9f55fc | passages:bank_2026_1_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-7f215d586d3bdac3b82baacd | passages:bank_2026_1_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-246c94da80fa14f8bc2b2019 | passages:bank_2026_2_1 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-a4ca3cdd06efbf224e661f78 | passages:bank_2026_2_2 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-d23ea8fbd4536c741901bccd | passages:bank_2026_2_3 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-19c14ba97eca3b8ce29d069e | passages:bank_2026_2_4 | passage_content_review | Human must compare passage text and provenance against the original source; machine checks do not approve content | {} |
| audit-893920a2730db18858865527 | questions:auto_366f70fa_q31 | location_pending | Human must verify evidence location | {} |
| audit-eb225e1e1ecaf947c182a40d | questions:auto_366f70fa_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d82081937bb9356b35dccb2a | questions:auto_366f70fa_q32 | location_pending | Human must verify evidence location | {} |
| audit-f2f4fd4c5d23bb1681be79eb | questions:auto_366f70fa_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-70f9b8d4c87504b836e25275 | questions:auto_366f70fa_q33 | location_pending | Human must verify evidence location | {} |
| audit-fb7c5ad55c286db65110047d | questions:auto_366f70fa_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ab2caa8f99d3738429b5529f | questions:auto_366f70fa_q34 | location_pending | Human must verify evidence location | {} |
| audit-cedac25e52a0fbe8eaef1f1b | questions:auto_366f70fa_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ed515016b4084994da47d894 | questions:auto_366f70fa_q35 | location_pending | Human must verify evidence location | {} |
| audit-bbebfb33d0d45ef7eefab417 | questions:auto_366f70fa_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0394392d9ebf1acd2d7b47c7 | questions:auto_51732c82_q26 | location_pending | Human must verify evidence location | {} |
| audit-e01a9a77569a1b7f92793cea | questions:auto_51732c82_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f9faf030b1f60393837119f3 | questions:auto_51732c82_q27 | location_pending | Human must verify evidence location | {} |
| audit-8516b2577bb3709c1b93f832 | questions:auto_51732c82_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5574e57e15344befd3ad48d4 | questions:auto_51732c82_q28 | location_pending | Human must verify evidence location | {} |
| audit-edc00f02d705e8b3ebe51a38 | questions:auto_51732c82_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f1488dfc0aaed2f0a8822574 | questions:auto_51732c82_q29 | location_pending | Human must verify evidence location | {} |
| audit-ea44bc37e7e2d7e9b53fe206 | questions:auto_51732c82_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3ad1303d7cb4b5ec55be7416 | questions:auto_51732c82_q30 | location_pending | Human must verify evidence location | {} |
| audit-74a2ae00998aff33dbe42420 | questions:auto_51732c82_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-34e0faab7e44312170df9653 | questions:auto_62abb41c_q31 | location_pending | Human must verify evidence location | {} |
| audit-9403f6f8fd9afde371358791 | questions:auto_62abb41c_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-71d8aa40d324370e84541e66 | questions:auto_62abb41c_q32 | location_pending | Human must verify evidence location | {} |
| audit-3811c3d4b8f458575785b4ab | questions:auto_62abb41c_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-6882dc89a3676d79f31079f9 | questions:auto_62abb41c_q33 | location_pending | Human must verify evidence location | {} |
| audit-7535ca1a608d20b19c511b8a | questions:auto_62abb41c_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2beb5e9a7b55dbe347fb5b62 | questions:auto_62abb41c_q34 | location_pending | Human must verify evidence location | {} |
| audit-6ff581a19000966322b209a2 | questions:auto_62abb41c_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-63c8b8af413b250d80d4a33c | questions:auto_62abb41c_q35 | location_pending | Human must verify evidence location | {} |
| audit-807be735ae40e4e0f249c702 | questions:auto_62abb41c_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-58b7ffc584ba703157a95b0f | questions:auto_8173a36f_q26 | location_pending | Human must verify evidence location | {} |
| audit-8886eaf61574cfb8ffc57a2c | questions:auto_8173a36f_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-50e14fe28ca178906e35cb3f | questions:auto_8173a36f_q27 | location_pending | Human must verify evidence location | {} |
| audit-69dd1f823cd2e20dac3e6d74 | questions:auto_8173a36f_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1c5b362210d76cbf04c8e3c5 | questions:auto_8173a36f_q28 | location_pending | Human must verify evidence location | {} |
| audit-2be29a80ace9f36210b6321f | questions:auto_8173a36f_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7f2fb152a4b587a85f43a398 | questions:auto_8173a36f_q29 | location_pending | Human must verify evidence location | {} |
| audit-1eb8dc99b92ff02194505d63 | questions:auto_8173a36f_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4955df657f81e75188165a33 | questions:auto_8173a36f_q30 | location_pending | Human must verify evidence location | {} |
| audit-49ccc73557d9719bb611a353 | questions:auto_8173a36f_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-bff4490b7c35eca40c43ef74 | questions:auto_8afe3a8d_q36 | location_pending | Human must verify evidence location | {} |
| audit-48108c6788fb8bd1f9913646 | questions:auto_8afe3a8d_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ff23b09fc950ba21e655fd40 | questions:auto_8afe3a8d_q37 | location_pending | Human must verify evidence location | {} |
| audit-d080a510232c976d4325c52b | questions:auto_8afe3a8d_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-19367cea561c9de63c62115b | questions:auto_8afe3a8d_q38 | location_pending | Human must verify evidence location | {} |
| audit-de400d09407f1beacb8b72d3 | questions:auto_8afe3a8d_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b8c5e2fd08d10b9b0d92fa49 | questions:auto_8afe3a8d_q39 | location_pending | Human must verify evidence location | {} |
| audit-64e2e118441597f3ef2b033f | questions:auto_8afe3a8d_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a7b18dc28846287a875d58fa | questions:auto_8afe3a8d_q40 | location_pending | Human must verify evidence location | {} |
| audit-fb4d7906c079ca63bd08aea4 | questions:auto_8afe3a8d_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-14c3e02b006eec5561410c41 | questions:auto_9ac36e62_q21 | location_pending | Human must verify evidence location | {} |
| audit-4f0a80c5399e5e6317a82163 | questions:auto_9ac36e62_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7d0c52c1c771bd8cb7201818 | questions:auto_9ac36e62_q22 | location_pending | Human must verify evidence location | {} |
| audit-96b050f0a56c83cfb628f4ea | questions:auto_9ac36e62_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e33a16c26383710a462abc10 | questions:auto_9ac36e62_q23 | location_pending | Human must verify evidence location | {} |
| audit-be8aabadc40c79cfc32c72b9 | questions:auto_9ac36e62_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-20558d9e3a3e2cd95d71e603 | questions:auto_9ac36e62_q24 | location_pending | Human must verify evidence location | {} |
| audit-50532bf0b98c92b46271a76f | questions:auto_9ac36e62_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a695dc0a69279094e0986d39 | questions:auto_9ac36e62_q25 | location_pending | Human must verify evidence location | {} |
| audit-7d51cf5435c28cccd60f95d5 | questions:auto_9ac36e62_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-15d0b264279c9ddf604a9b1a | questions:auto_f76e487c_q36 | location_pending | Human must verify evidence location | {} |
| audit-ed629010e389a7f5a9234ed5 | questions:auto_f76e487c_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d1b64aa6ba0671a49bfc3093 | questions:auto_f76e487c_q37 | location_pending | Human must verify evidence location | {} |
| audit-83bfb334aedc5ce7e4de0edb | questions:auto_f76e487c_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5fc1e4ad4e2e4eb3c03f4198 | questions:auto_f76e487c_q38 | location_pending | Human must verify evidence location | {} |
| audit-772d97e22c74ad400ee2caed | questions:auto_f76e487c_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-45e5f90fc7973fa1c6201a6c | questions:auto_f76e487c_q39 | location_pending | Human must verify evidence location | {} |
| audit-1e1d5b01a8f3e8445631b478 | questions:auto_f76e487c_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f4ffadd3f662b6c9912137c4 | questions:auto_f76e487c_q40 | location_pending | Human must verify evidence location | {} |
| audit-61c964f6475adeb5d1b1725b | questions:auto_f76e487c_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f4955b8e528cfe4713140a7e | questions:auto_f81c35a0_q21 | location_pending | Human must verify evidence location | {} |
| audit-355c15c5eb0d6b6986b9aee0 | questions:auto_f81c35a0_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-753f4ec86ddf98155e216f82 | questions:auto_f81c35a0_q22 | location_pending | Human must verify evidence location | {} |
| audit-fff10fce268d807817785d19 | questions:auto_f81c35a0_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-da6fc434e2832d585d13f92a | questions:auto_f81c35a0_q23 | location_pending | Human must verify evidence location | {} |
| audit-b4c65972cf6e4e7d34cdb046 | questions:auto_f81c35a0_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-34e9a3e9b01667c403ae4027 | questions:auto_f81c35a0_q24 | location_pending | Human must verify evidence location | {} |
| audit-1ff33a1d65c0b68b44e2b7d5 | questions:auto_f81c35a0_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-be24a8e38341f25f5eb34816 | questions:auto_f81c35a0_q25 | location_pending | Human must verify evidence location | {} |
| audit-dcfd2c829f47292d91572350 | questions:auto_f81c35a0_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-13f32e5d03c16cba7366230e | questions:bank_2018_1_1_q21 | location_pending | Human must verify evidence location | {} |
| audit-8ebdddb356d4dd220f494001 | questions:bank_2018_1_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-40a91276c276f72449104bcc | questions:bank_2018_1_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-8eaed73d58fafd05a578fb2d | questions:bank_2018_1_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-911dcd0b99b92a9d724863dc | questions:bank_2018_1_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4c4375221352c0a98f3471eb | questions:bank_2018_1_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-238ca3d5f548645965f60ded | questions:bank_2018_1_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-30875db7b7f6cbc272afc0b8 | questions:bank_2018_1_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1c0750fc6d9bb01bd8cd4bce | questions:bank_2018_1_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-fab4839a82fe857b6e183d72 | questions:bank_2018_1_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9739eb77c2eaeb952cc27826 | questions:bank_2018_1_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-022870669bcf99544958a563 | questions:bank_2018_1_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-ab0b1690abfc5f8a250be7c9 | questions:bank_2018_1_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-28325d3fddbcdca0e96b9c20 | questions:bank_2018_1_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-6c6905850a89775f95f78edb | questions:bank_2018_1_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9561c5019c4c87ad6e1073c1 | questions:bank_2018_1_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-8b519a87f2e144eac0cea56c | questions:bank_2018_1_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-cef3f045bf2e1dfb56058563 | questions:bank_2018_1_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e6b8b1039ea6888f922931e9 | questions:bank_2018_1_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-29a5e7130b26c43135357bf7 | questions:bank_2018_1_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-db5d29c1a7da956bed43d0ee | questions:bank_2018_1_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-20324998d1eff0024b7f224e | questions:bank_2018_1_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-2b926f0b5ce37af9f99879fb | questions:bank_2018_1_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1b8f695f61c1e236c8b2d722 | questions:bank_2018_1_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0902e02055418884afd4580c | questions:bank_2018_1_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-62759786af0db703af677ba1 | questions:bank_2018_1_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c435e637a451eee8b4c9519b | questions:bank_2018_1_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-f98350f5b692229fd4e4c774 | questions:bank_2018_1_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-97b679715cfe6e5e3b3feb55 | questions:bank_2018_1_4_q39 | location_pending | Human must verify evidence location | {} |
| audit-3b5139a3edf96612469a0499 | questions:bank_2018_1_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-72e8f1ae362001523826a45b | questions:bank_2018_1_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-58c3511b27b72a9f23b07b80 | questions:bank_2018_1_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-eac0cb54f80b44042517b129 | questions:bank_2018_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-beea2913a5e8bde743b43132 | questions:bank_2018_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0b75183713fb23630b5ed307 | questions:bank_2018_2_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-b017dec61fcd4a26bd2e5d8c | questions:bank_2018_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dd9fc70352ffecb5ad7786af | questions:bank_2018_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c1c2fb2479b68fa20bb30db6 | questions:bank_2018_2_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-a57548b26fe8f208cf4dfe5a | questions:bank_2018_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5460ad2e73bf5d2355a8d9e7 | questions:bank_2018_2_2_q26 | location_pending | Human must verify evidence location | {} |
| audit-ce1d489cfd659aa3e0cdf593 | questions:bank_2018_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-752bed2eb74af8228bf952e5 | questions:bank_2018_2_2_q27 | location_pending | Human must verify evidence location | {} |
| audit-31a1179db29ea95c429ca7bd | questions:bank_2018_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3761f3e1759f02416f903851 | questions:bank_2018_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dc7c1ce2fecd3ccde9d47400 | questions:bank_2018_2_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-440f73a75d06a2c331e5f975 | questions:bank_2018_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-11f56bf9c94d5b5192c9f405 | questions:bank_2018_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b173b3115b19c5c46ed03834 | questions:bank_2018_2_3_q31 | location_pending | Human must verify evidence location | {} |
| audit-28dbe2b16c69d98c265e9971 | questions:bank_2018_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-516e84e2ab19c334984d3ccb | questions:bank_2018_2_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-89e4f1f495f34d1299800053 | questions:bank_2018_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3cb541b8db40d083d20019d4 | questions:bank_2018_2_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-f4a421052a854d34bb743b4b | questions:bank_2018_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-6fed3a9a4cecba456d5e456c | questions:bank_2018_2_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-182ffd28a585715a907f0c7a | questions:bank_2018_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4a03c0ffad803ebf08da3b9e | questions:bank_2018_2_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-d66d5a07b904829c2c75dfea | questions:bank_2018_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-087cc13bf2141b825eee6a94 | questions:bank_2018_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3afb3272300bd4d0f9eb8fef | questions:bank_2018_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c9e51e971ef3ca96f48dfb1c | questions:bank_2018_2_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-45c938f91abdaeaa64104c9a | questions:bank_2018_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-36c8be1ceef76e86002e0c31 | questions:bank_2018_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a9771686de8ef15627b50c96 | questions:bank_2018_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-78b6cc4e54a4957ac3c98145 | questions:bank_2018_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-cc044373673b85c89b3a5b84 | questions:bank_2019_1_1_q21 | location_pending | Human must verify evidence location | {} |
| audit-4bbcc56b3b28ef05aa25ac57 | questions:bank_2019_1_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d91c5f420b36624b8594d07d | questions:bank_2019_1_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-c14bc24dee5b214d79b70b24 | questions:bank_2019_1_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ac7ba4822fc9d8f149b8d27f | questions:bank_2019_1_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-25c57923728552c3ef04e9db | questions:bank_2019_1_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-29facfd314cc85f073767263 | questions:bank_2019_1_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-af9eb3561c21291a60de20ec | questions:bank_2019_1_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-6b10a74b633d925081ba7270 | questions:bank_2019_1_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9caa6bbd775d23a226276549 | questions:bank_2019_1_2_q26 | location_pending | Human must verify evidence location | {} |
| audit-df09745693f2cf0a6cfcb0d9 | questions:bank_2019_1_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b8eb81f48995e67c6479d6a3 | questions:bank_2019_1_2_q27 | location_pending | Human must verify evidence location | {} |
| audit-b51c29d6df448ec9c9d415f5 | questions:bank_2019_1_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b371b973512047b58c3e59ab | questions:bank_2019_1_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3825f885ddae10f5abd32355 | questions:bank_2019_1_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-8a99453c5c0378946cb32d03 | questions:bank_2019_1_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9d725dc2fccae2fbddf81d4c | questions:bank_2019_1_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-5de79de3a9e55f158fe4a609 | questions:bank_2019_1_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-92d2f030615c1b9b7265dc20 | questions:bank_2019_1_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a73535ef549c3354cb491d1d | questions:bank_2019_1_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-8924a51982aef34f013a5d9f | questions:bank_2019_1_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-35a3dc755689f113b870d13f | questions:bank_2019_1_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-d671c25482634c5d37fc01a9 | questions:bank_2019_1_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-333d1d092d465b7bc839a92c | questions:bank_2019_1_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-544f832bb742d9c332886c23 | questions:bank_2019_1_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-825e01497b04a4dc02a12637 | questions:bank_2019_1_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-52d367d99c59ec01a4793a12 | questions:bank_2019_1_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-71a41511303b8f5268be222d | questions:bank_2019_1_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a077917008b82c00072c6e56 | questions:bank_2019_1_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-08ac68c22527f4e0fdc45b08 | questions:bank_2019_1_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-6f3714a4344551f2a2651c17 | questions:bank_2019_1_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-75f582d33bc74685c6b4bd4d | questions:bank_2019_1_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-23eb225fc829f53a3a1286dd | questions:bank_2019_1_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-7868ee5ad60ed24acc95ae45 | questions:bank_2019_1_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4c7919067c6614e6e0c9c69d | questions:bank_2019_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b8eeca93dc482eab99afb2e4 | questions:bank_2019_2_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-3a67982502114f4fee6b9239 | questions:bank_2019_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7e1c6e0b6258d1acd40605ed | questions:bank_2019_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7f410b33a4e61ccde4ba5a8c | questions:bank_2019_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c28ffd3052734c21db525c65 | questions:bank_2019_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ab903e5e341eb1b114c8ad28 | questions:bank_2019_2_2_q26 | location_pending | Human must verify evidence location | {} |
| audit-e4191e2c598cec7245842397 | questions:bank_2019_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1f58b545d2ff6a01917fcc3b | questions:bank_2019_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-96bf39a386fe4476fa6c5d1a | questions:bank_2019_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7a9132e01e992cebdbb12e5b | questions:bank_2019_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a0919241688cbb20980dabfd | questions:bank_2019_2_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-bcc4081bc6eb428d1027cb77 | questions:bank_2019_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-aa026e3a8c39504656a20252 | questions:bank_2019_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ab432e4ce4ddb7c125a9096d | questions:bank_2019_2_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-c8f2e7169d051f77c520a4ca | questions:bank_2019_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a5286aed8487fc74acc81ce1 | questions:bank_2019_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d5a6ccb2e0b7ac85e642b8c2 | questions:bank_2019_2_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-55f5273c5c41ae154f8db016 | questions:bank_2019_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d02a3c069fbac0652c511296 | questions:bank_2019_2_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-bacfe55ecdc52903fa1dcc1d | questions:bank_2019_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-873069cc200cecaa65b23637 | questions:bank_2019_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b2a6d43a1cc54fe4e0442784 | questions:bank_2019_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1b87bfcff25a7b2dc400e025 | questions:bank_2019_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4be627c4492dfdb1748f155b | questions:bank_2019_2_4_q39 | location_pending | Human must verify evidence location | {} |
| audit-6e18be2355da2bf69d8a3746 | questions:bank_2019_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c3f78fc5e5c43eb8b3a40664 | questions:bank_2019_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-e7da83c3af92c4a035ddb2ae | questions:bank_2019_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9f4e8032d12a111e59a1dd65 | questions:bank_2020_1_1_q21 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-16dab36fecfc6f2359c981ea | questions:bank_2020_1_1_q21 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-b1686b5244edb05e225e9676 | questions:bank_2020_1_1_q21 | location_pending | Human must verify evidence location | {} |
| audit-a7ebe95960d026d6e6c36d71 | questions:bank_2020_1_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f6d51657ca21910eb6543910 | questions:bank_2020_1_1_q22 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-5cecdd216266770d1ec6505f | questions:bank_2020_1_1_q22 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-7dc856b3a0723704e971507d | questions:bank_2020_1_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-1cb2cb23b507ce3de85ccc60 | questions:bank_2020_1_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-97dfff1fdac39b75d30d6744 | questions:bank_2020_1_1_q23 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-6553d8d87226878e7a9c5567 | questions:bank_2020_1_1_q23 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-26605843e215425bd296fa90 | questions:bank_2020_1_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-2cfe4bb8c2cd1068287bb89b | questions:bank_2020_1_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-87968ef97c1d0fffe719d87d | questions:bank_2020_1_1_q24 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-a01125a81d1331dc9ee19808 | questions:bank_2020_1_1_q24 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-fda6c6720496565b8392b9b2 | questions:bank_2020_1_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-769a5cfee7c732f2fd940e8f | questions:bank_2020_1_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ec89dc492eef71b83d629ead | questions:bank_2020_1_1_q25 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-dfd1fc7bd87bd2cc2cc89660 | questions:bank_2020_1_1_q25 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-fc8693df82128459e7720cb0 | questions:bank_2020_1_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-8ee7e4e3d9a4d9247a21e083 | questions:bank_2020_1_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-214dc923c0cb6256ec4a6b4c | questions:bank_2020_1_2_q26 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-2ed8bd509199f2ed2db9777f | questions:bank_2020_1_2_q26 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-1d1158a1b1f7c2a2dd1e8e99 | questions:bank_2020_1_2_q26 | location_pending | Human must verify evidence location | {} |
| audit-876ef16263c7a0b6efa84f5e | questions:bank_2020_1_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0686053400c4e57f4905e415 | questions:bank_2020_1_2_q27 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-9d4a85fb8c2cc8b5a1009957 | questions:bank_2020_1_2_q27 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-2daf7630aabbcf6488341102 | questions:bank_2020_1_2_q27 | location_pending | Human must verify evidence location | {} |
| audit-b6ed6601d2048679739ee372 | questions:bank_2020_1_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2945c5f5100f18274ec9c36c | questions:bank_2020_1_2_q28 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-8dd7adf773578ef9a8dd3d0d | questions:bank_2020_1_2_q28 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-f8556e4a031185075d198e79 | questions:bank_2020_1_2_q28 | location_pending | Human must verify evidence location | {} |
| audit-7c4bfe303c1e1376a633cb60 | questions:bank_2020_1_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-63d87269c5674045b961b46d | questions:bank_2020_1_2_q29 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-f0dff54171a976b9f020de0d | questions:bank_2020_1_2_q29 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-3b02a2168273b77a4712d353 | questions:bank_2020_1_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-b60a65101827d4222cb8b6db | questions:bank_2020_1_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9c04bc82dfcf8a6b5ee95dbe | questions:bank_2020_1_2_q30 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-550dac0c6cb469be58c545d4 | questions:bank_2020_1_2_q30 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-064147585dd4a247a735c924 | questions:bank_2020_1_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-a733c26bce35f8c871d52444 | questions:bank_2020_1_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b7416c440b87b8c6bf7d1cac | questions:bank_2020_1_3_q31 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-a5233ffbbb686c852ad4dcaf | questions:bank_2020_1_3_q31 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-b339b176b9f47cddbc11d376 | questions:bank_2020_1_3_q31 | location_pending | Human must verify evidence location | {} |
| audit-42bd9ceee1817e83de8177b6 | questions:bank_2020_1_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c2e6d4054261761e83079c68 | questions:bank_2020_1_3_q32 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-70985f0b9445cffd933db247 | questions:bank_2020_1_3_q32 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-d03f1d51c65edd4400dd333a | questions:bank_2020_1_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-2ebde4dc412b9beba09c739f | questions:bank_2020_1_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f58bd99ab16041ed879dcd7f | questions:bank_2020_1_3_q33 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-5809c968456fc561542a650c | questions:bank_2020_1_3_q33 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-cdce16cc73f601b410902567 | questions:bank_2020_1_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-b063d06c83506f52d49c5f62 | questions:bank_2020_1_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c00364ee172db1b30db3e750 | questions:bank_2020_1_3_q34 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-e05206f48be2776f1d538b2e | questions:bank_2020_1_3_q34 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-b424cef4c8093cce6156e615 | questions:bank_2020_1_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-dc860e6b0ff8b77ae2eb4d8e | questions:bank_2020_1_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-6db61fd344c330631e922003 | questions:bank_2020_1_3_q35 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-0d31f0fa08363fcead099fcb | questions:bank_2020_1_3_q35 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-f91ce6f3b594c83bf5bb3718 | questions:bank_2020_1_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-e6cca776cbc1837d735742a0 | questions:bank_2020_1_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5e4bb3f1261821bdafc7a08f | questions:bank_2020_1_4_q36 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-67ce8ad05116f429c704d4ea | questions:bank_2020_1_4_q36 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-87ff4ea95603ab83ec5d8fe5 | questions:bank_2020_1_4_q36 | location_pending | Human must verify evidence location | {} |
| audit-e8a5c7bff24819492c325072 | questions:bank_2020_1_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-857aae7a0278dda6de6152ed | questions:bank_2020_1_4_q37 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-ecc6f83a9842d28dc2223192 | questions:bank_2020_1_4_q37 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-63447ef18679fc69918b5eab | questions:bank_2020_1_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-6729f45123dd397b340705af | questions:bank_2020_1_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d8d5661e1d80efaacf0236be | questions:bank_2020_1_4_q38 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-3eb902888cf286a5c0877f76 | questions:bank_2020_1_4_q38 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-8b736f7687f2839480c02b71 | questions:bank_2020_1_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-b1ef86bb773dcf402fa54dce | questions:bank_2020_1_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0bac0629fef2c8d3c6513c18 | questions:bank_2020_1_4_q39 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-7c026a203ff1645557db828a | questions:bank_2020_1_4_q39 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-9b09d25682811c14f0f754bb | questions:bank_2020_1_4_q39 | location_pending | Human must verify evidence location | {} |
| audit-45775a91e4ef9888250419fa | questions:bank_2020_1_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-09f71b1d37e4b961c697c86f | questions:bank_2020_1_4_q40 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-ad420c3960623627d95e04cb | questions:bank_2020_1_4_q40 | analysis_needs_review | Human must supply/check explanation and reasoning steps | {} |
| audit-1329a473a272d49e068ebc08 | questions:bank_2020_1_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-8d11283c6ab105a662ff7c0b | questions:bank_2020_1_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-50d0af60a799ffac24a60c66 | questions:bank_2020_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1bd02556a253fdd09e0d93dd | questions:bank_2020_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1ae0586e563d2a5a67e3f173 | questions:bank_2020_2_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-8522a43b81f2d09608aa84e0 | questions:bank_2020_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1dfbf8c07821e5e90f7349ad | questions:bank_2020_2_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-8b5c6cfe56096abb261292ab | questions:bank_2020_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a4df0ce2de4204cb66a9632d | questions:bank_2020_2_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-36f57d9ba85cee5721563319 | questions:bank_2020_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c8b194fa4413c562e31f05e7 | questions:bank_2020_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-009295cf522f899b01a408fc | questions:bank_2020_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b0c7fac29e4295ffea24bbb8 | questions:bank_2020_2_2_q28 | location_pending | Human must verify evidence location | {} |
| audit-14eb8a1b6f3e92eded6de89e | questions:bank_2020_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-943d8c9a84f448046d43e72d | questions:bank_2020_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-67213e8592aecc84b404b824 | questions:bank_2020_2_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-be5328d40fcf17cd53ba5714 | questions:bank_2020_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2cc623fb445c2ea35626e34e | questions:bank_2020_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-de4490ac04bf330b27955d2b | questions:bank_2020_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-aaf2521bdff68c4c6c0d4a15 | questions:bank_2020_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-bb92711f79cebd6093d968ab | questions:bank_2020_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f009ae757694ace48e0ce1c1 | questions:bank_2020_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dafd849736eb3221530d1934 | questions:bank_2020_2_4_q36 | location_pending | Human must verify evidence location | {} |
| audit-239b02a6b5caf1307fe7035a | questions:bank_2020_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-cecc3dc954f750ba46c9a2c3 | questions:bank_2020_2_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-03374abf658570e9ac35190a | questions:bank_2020_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f65af01ef92c845681a4a2a7 | questions:bank_2020_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-58e7f7d7c9550f85e192e904 | questions:bank_2020_2_4_q39 | location_pending | Human must verify evidence location | {} |
| audit-e0047623f3519ae411b2a112 | questions:bank_2020_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4a8d10b20cfe3d6eab72e0fb | questions:bank_2020_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-69b1c8044ef0df3ecd4d3ca1 | questions:bank_2020_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c8634028bef4a6a6c311920f | questions:bank_2021_1_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-bb5f958051d276b4ec8ce9dc | questions:bank_2021_1_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-afb42980506ec79262655ec0 | questions:bank_2021_1_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-91ce852b34e7233694fdf45d | questions:bank_2021_1_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-33b7945a6a7faa89dca2ce57 | questions:bank_2021_1_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0746a6f3f16ba58a4423a58f | questions:bank_2021_1_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-cd4e8e061a37a799098a473d | questions:bank_2021_1_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d73bc3321bf45e6e480077f9 | questions:bank_2021_1_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3d2c7eaf77f5000600e63988 | questions:bank_2021_1_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-08d7580e12c3ac42047f21fd | questions:bank_2021_1_2_q28 | location_pending | Human must verify evidence location | {} |
| audit-2b23da9d90be9704eb1253c8 | questions:bank_2021_1_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-593f20f519c53bf73a2198a0 | questions:bank_2021_1_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-22c283c155bd1579161e2243 | questions:bank_2021_1_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4c459d03c64b0f9acc352d4f | questions:bank_2021_1_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-5b118a5431c556968f16e703 | questions:bank_2021_1_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5103359ada50478e9fde7d07 | questions:bank_2021_1_3_q31 | location_pending | Human must verify evidence location | {} |
| audit-591f8f810d39849e8f18c795 | questions:bank_2021_1_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b71c6147ae80a855b876c589 | questions:bank_2021_1_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-34163e14ad9e400eb6e80445 | questions:bank_2021_1_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-77b5323c6cfb3bc1ef5e7da3 | questions:bank_2021_1_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-52c6889686532dd3d152db72 | questions:bank_2021_1_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-7574ecd9e32542b12217ae71 | questions:bank_2021_1_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-68341ec4248fa4025bada71a | questions:bank_2021_1_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-8addcf8ee09597f03e7d0aa1 | questions:bank_2021_1_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-70d99c3c54e5d35d40915e02 | questions:bank_2021_1_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-71d99ace493f94724d72f5ca | questions:bank_2021_1_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-61db965d073a21c14cfc61bd | questions:bank_2021_1_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-41600ff2bc7a8cac0fc9cf47 | questions:bank_2021_1_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-706cb87b86a85ca9005f9006 | questions:bank_2021_1_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3e95e0e427213bc8e2072876 | questions:bank_2021_1_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-60f379d2d6fe17c7dc81551b | questions:bank_2021_1_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-5000bd0f88425685db4c52f5 | questions:bank_2021_1_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-36022e8a9aba71381ae325d5 | questions:bank_2021_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3351745575fad4606ce5bf81 | questions:bank_2021_2_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-d991d8cb42074f83927898a2 | questions:bank_2021_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c2b917003ef4c30f3e21bbfb | questions:bank_2021_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-39796cd78ea92faec479c306 | questions:bank_2021_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-862b0204a7b82f9b8811917b | questions:bank_2021_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-8f2e85bcc82753bcdc61ea8b | questions:bank_2021_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ad527a6563d5b888cb901cbd | questions:bank_2021_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ed5a8471669ff1813cfdc41d | questions:bank_2021_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-69d719c9675a7b627ffcc175 | questions:bank_2021_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-6ee003215f6a304c3b44bc8e | questions:bank_2021_2_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-a97052653617c3be1c101afa | questions:bank_2021_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-89d377dc59555519a8cdcbeb | questions:bank_2021_2_3_q31 | location_pending | Human must verify evidence location | {} |
| audit-7940a0f7fe29ddd408918171 | questions:bank_2021_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-44e3429999e13d2dbcf14afb | questions:bank_2021_2_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-661b5062f340eac169ba2a9e | questions:bank_2021_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dc46d0a52993ff9a347172c7 | questions:bank_2021_2_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-02ec285eff95564fa11371c9 | questions:bank_2021_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a6d927eeb5a75beb4207fcd4 | questions:bank_2021_2_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-6371fe7461d8ee443e40075d | questions:bank_2021_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9f09744bbaa2716faec27795 | questions:bank_2021_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2d781d7d59872be8def74a47 | questions:bank_2021_2_4_q36 | location_pending | Human must verify evidence location | {} |
| audit-87da024d369c2d56ba55d90e | questions:bank_2021_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2b5c1c4ee81b3122ada50507 | questions:bank_2021_2_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-1ce1337dd1648078ef38c14d | questions:bank_2021_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-bba7454e3731bf5e59b4b7d8 | questions:bank_2021_2_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-4bfcfbeaed749f0045d98c39 | questions:bank_2021_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-221e5c5d69c7ffa948ba1c97 | questions:bank_2021_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5523262764228bcf7f6aca21 | questions:bank_2021_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-33497aedb68f64cd01063aa2 | questions:bank_2021_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e1d4bfddf8782fda24506584 | questions:bank_2022_1_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3c98b06a133f12458fabe140 | questions:bank_2022_1_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-99cc29126c5d17338dee6f2e | questions:bank_2022_1_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9353a0c45b1a6a9531e229a2 | questions:bank_2022_1_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-459bc1192979a0b5bdd58174 | questions:bank_2022_1_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c9b35a89147c782fc3ec2fdb | questions:bank_2022_1_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-fad62133ba595dca81ec866a | questions:bank_2022_1_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-1a35e13eac5a68c449e409e2 | questions:bank_2022_1_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-74b9543fde149f93e4d4483a | questions:bank_2022_1_2_q26 | location_pending | Human must verify evidence location | {} |
| audit-b3e44cbae9b94b0eee27656a | questions:bank_2022_1_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-481b0119c7553ea0fb70ab99 | questions:bank_2022_1_2_q27 | location_pending | Human must verify evidence location | {} |
| audit-f926006563ed930107c04e9f | questions:bank_2022_1_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-28ea10a6d666a6f11bc610b0 | questions:bank_2022_1_2_q28 | location_pending | Human must verify evidence location | {} |
| audit-4a013c5a342041761b41af96 | questions:bank_2022_1_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1d8d0c254c09d5fffd3a8faa | questions:bank_2022_1_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-ffbf42f508ab844652028a70 | questions:bank_2022_1_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2a9b04b7e51e9def117e7aba | questions:bank_2022_1_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-273239a8253fd9b1e5d6e801 | questions:bank_2022_1_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d3ab75268a01d8102ac5b3f3 | questions:bank_2022_1_3_q31 | location_pending | Human must verify evidence location | {} |
| audit-2af5abcb7edb05010722e048 | questions:bank_2022_1_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a0c1d39461e0bbc0cb4e8083 | questions:bank_2022_1_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-1031b417e87c63b57a4943dc | questions:bank_2022_1_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d5410e59273cdeb9e89be865 | questions:bank_2022_1_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-8f9ff1a8c748c9842c2204fb | questions:bank_2022_1_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-423d3f191bf9db61e3a501e3 | questions:bank_2022_1_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-ff30a1a61835752119dd7eeb | questions:bank_2022_1_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-26200b78c28ea50f70dc23c0 | questions:bank_2022_1_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-6015b743d5413add94b3675a | questions:bank_2022_1_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2dfc2e184e85f36db9f9949d | questions:bank_2022_1_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-69c10026e0262281f530c277 | questions:bank_2022_1_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-55459678f56fa2d4886313ec | questions:bank_2022_1_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-67460ad06997443fc1aa7aab | questions:bank_2022_1_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-cb5394567007dd95abcf88df | questions:bank_2022_1_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9502a37f66c775e3cacfa74c | questions:bank_2022_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5db4b78ca128b3ac8aa065c8 | questions:bank_2022_2_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-9f1bc045c70878d4cfa535aa | questions:bank_2022_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-8e1996310b618870f8c1cff4 | questions:bank_2022_2_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-fdd24f254233c07c8820e274 | questions:bank_2022_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-872e4df50b84f0e64c6aa89d | questions:bank_2022_2_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-0d0f098847c7de4cb14ceca7 | questions:bank_2022_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b189c37a2cfe0fcad1dd73d3 | questions:bank_2022_2_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-5970bc03fab2baa35a941c9c | questions:bank_2022_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-8ed7200d8d6f75a59344376e | questions:bank_2022_2_2_q26 | location_pending | Human must verify evidence location | {} |
| audit-a5a03a78f4fc15c579a7c8af | questions:bank_2022_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dae044be7feeeb9dee32119a | questions:bank_2022_2_2_q27 | location_pending | Human must verify evidence location | {} |
| audit-0f8d32f6cbe6a19cfc150bbf | questions:bank_2022_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-04ff7b22ee29a834a04ddaaf | questions:bank_2022_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d5d91b82f8c1211a4d08eb03 | questions:bank_2022_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-fe8ab80212191572b3c44c93 | questions:bank_2022_2_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-b03c726076201b3026c62141 | questions:bank_2022_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-df673a3aab7237bf10e2afa5 | questions:bank_2022_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-efde53a4b7c15eccfd03e463 | questions:bank_2022_2_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-388a37a0e60fde5cfe7d1818 | questions:bank_2022_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7983b66ad37d949072da36ed | questions:bank_2022_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-665d98c44f54a306ee2b8035 | questions:bank_2022_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-66297a7a86a40d1110203bec | questions:bank_2022_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ac9d03171f81c36055722e6b | questions:bank_2022_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d30088b8da056864802487f7 | questions:bank_2022_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-30781898ddf0435c2c4fcea8 | questions:bank_2022_2_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-17c0e03068746cb386e69bc0 | questions:bank_2022_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-23434bff31dafcd7bab4e601 | questions:bank_2022_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-53c833df8803836145ec6c08 | questions:bank_2022_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-398834ea6fed6412d004198a | questions:bank_2022_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7e69b92c747edafe0ada7a2c | questions:bank_2023_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5166780869727dece5c9c115 | questions:bank_2023_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-751869c87de23a8eb2d755b5 | questions:bank_2023_2_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-ec32dd278c80f604b5c7537a | questions:bank_2023_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b2f5eaf086576bacb77702ba | questions:bank_2023_2_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-53ad38a5ef7896af5a5a8ae0 | questions:bank_2023_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-35fc13c049a240418b129820 | questions:bank_2023_2_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-30ef9cac3dd2a6b8c36a858f | questions:bank_2023_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-23f0382eb0a6993d9ecfd9a5 | questions:bank_2023_2_2_q26 | location_pending | Human must verify evidence location | {} |
| audit-40df438efe23a226f771b360 | questions:bank_2023_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-cd175c5d2c15cb645fa7b020 | questions:bank_2023_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-65d3a9cdb6b125393ab17ef8 | questions:bank_2023_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-11af3023911d85ad3b09b978 | questions:bank_2023_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9e1146a0c655d98ec5535212 | questions:bank_2023_2_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-3bf50330f52ab2ee52a00167 | questions:bank_2023_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-37971e81d646921b806b61e4 | questions:bank_2023_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1efe0595e50ef74b45e0a67e | questions:bank_2023_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-87b42d6fd360818ce6ad242b | questions:bank_2023_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-bf9defbd57e7487389a071b5 | questions:bank_2023_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d18c1f8018f0d367b4d107d3 | questions:bank_2023_2_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-b81a6c5e662c855a6908ef63 | questions:bank_2023_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-bdf118b1264116a196b96989 | questions:bank_2023_2_4_q36 | location_pending | Human must verify evidence location | {} |
| audit-dff8a668a98d0fc40cfce057 | questions:bank_2023_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-647c420e8d67cbcb0f5f02ef | questions:bank_2023_2_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-980e9b9efd9dc870fdebc3d9 | questions:bank_2023_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d5f05d31d832f0327b801906 | questions:bank_2023_2_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-95cbb0ce79ee732f6df21abf | questions:bank_2023_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a78f5da15740b64d11e7ed07 | questions:bank_2023_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ee72686ed565c9b00be832df | questions:bank_2023_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-36b1199030046dad43d34956 | questions:bank_2023_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-792cb7cc7c7d56da2f9c0e10 | questions:bank_2024_2_1_q21 | location_pending | Human must verify evidence location | {} |
| audit-e25a4a6e428b166b5f6ec1ac | questions:bank_2024_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-bf0b0731d7d6dee0f3ddf80a | questions:bank_2024_2_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-a20022b585fa04409ec3dc9b | questions:bank_2024_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f0f7f22ab99e9f1f4aef1273 | questions:bank_2024_2_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-15257ca18b80e2d4d3373f04 | questions:bank_2024_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a34dd049b8fb371311fef592 | questions:bank_2024_2_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-b5bafbb7e8c9237ac9b066ea | questions:bank_2024_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3859a11d40d93522a849f75b | questions:bank_2024_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-72c23bc3ed7bd67371c7bc12 | questions:bank_2024_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-117e7d87562f6d3a6dda53ea | questions:bank_2024_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9384b52c2bc0ff460e2b14f6 | questions:bank_2024_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-12a08817b73c0f9198887f1b | questions:bank_2024_2_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-4d7f17524292e525f7827675 | questions:bank_2024_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-8474bb6cad58a1286e9a5518 | questions:bank_2024_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ac0930da6a1e351109b27d44 | questions:bank_2024_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-35b959c5616f2c22378f8356 | questions:bank_2024_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9ddebb6d73a8c89bad0f8aa7 | questions:bank_2024_2_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-f3176f2a081ed6e811cd4f1a | questions:bank_2024_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-555a38474c6021e6d11aeaed | questions:bank_2024_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3c8346866ba6675bfbd62653 | questions:bank_2024_2_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-b9f6ce44cbac8ff6b48a0cce | questions:bank_2024_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7bc5dd090ca007e2424fc07c | questions:bank_2024_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-891298fe248b7ce2d0d09a9a | questions:bank_2024_2_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-49ff35ecbf2173f11c64fe51 | questions:bank_2024_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dfd391ee4cf76cdc13688a71 | questions:bank_2024_2_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-4d45eed4e65a6d15c2fb487e | questions:bank_2024_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-8ef10afeda182ece0cbdad40 | questions:bank_2024_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5c50040d3b1fa927b3ab2732 | questions:bank_2024_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-9eb66380f2a93b98a4a640f3 | questions:bank_2024_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5067c5afde3e32163c91d3a3 | questions:bank_2025_1_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-17d317aedd48df8ae05a2b94 | questions:bank_2025_1_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-056f5923adfec623bb481c14 | questions:bank_2025_1_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e6685ec189460e76ca55e836 | questions:bank_2025_1_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-af93b4520815aacac7356d39 | questions:bank_2025_1_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-fb16dbbf22451644960a0f5f | questions:bank_2025_1_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-6d619b0f98b590e5e45b87ae | questions:bank_2025_1_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-28762ff57b46f5a1c4833b44 | questions:bank_2025_1_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-bcb5a516456cabaee70d067f | questions:bank_2025_1_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-249f5b5349c4cf6e956febf6 | questions:bank_2025_1_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5b074aa7ff579496e2e40027 | questions:bank_2025_1_2_q27 | location_pending | Human must verify evidence location | {} |
| audit-e41910f7d0742678cdb8544e | questions:bank_2025_1_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-89c50276a0b296b3557c96ff | questions:bank_2025_1_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d5078ead72ec8612149c901b | questions:bank_2025_1_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-795456eb0016dfc2bb1aa018 | questions:bank_2025_1_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b33c8947c9b05ee40dbe2239 | questions:bank_2025_1_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-0736bedf0d9d99be901156f0 | questions:bank_2025_1_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f481d96f8ec5573d4ecd0e24 | questions:bank_2025_1_3_q31 | location_pending | Human must verify evidence location | {} |
| audit-67422417265f9fb5d65dd229 | questions:bank_2025_1_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f127b02a07be934c6e5d5afd | questions:bank_2025_1_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0194de02779733d753e1c3c5 | questions:bank_2025_1_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-6d91bf22124c732a934bb6b7 | questions:bank_2025_1_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-622b8fc4a5dd6d281fae79c6 | questions:bank_2025_1_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-a9f9ff5608f25b4075921c7a | questions:bank_2025_1_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7e11eda7822951b370eb9e8e | questions:bank_2025_1_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-3abcf24b03cf3f2593fa34c3 | questions:bank_2025_1_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ca4c0523c0a1788c55858d87 | questions:bank_2025_1_4_q36 | location_pending | Human must verify evidence location | {} |
| audit-5892d7cd9ce401fe392f43c0 | questions:bank_2025_1_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1f563b7228a53077a7e67a9b | questions:bank_2025_1_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3509114e6159d4b4d2051069 | questions:bank_2025_1_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ba973d963db5df127b2a4458 | questions:bank_2025_1_4_q39 | location_pending | Human must verify evidence location | {} |
| audit-8129a2e931cb699905649b03 | questions:bank_2025_1_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d9d2adeba39b5390da6a523f | questions:bank_2025_1_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-4ec2eb9689fb675546648ef2 | questions:bank_2025_1_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-5622d38a7b997dee4b5a1a26 | questions:bank_2025_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-fd37c4d9eeeda25344ce1a32 | questions:bank_2025_2_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-50c8d08fa608c5449d05ece5 | questions:bank_2025_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-8595a921c784c05db35d7881 | questions:bank_2025_2_1_q23 | location_pending | Human must verify evidence location | {} |
| audit-866dfbd78c677c45de55054f | questions:bank_2025_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0a3c94fda1363908cfe193e0 | questions:bank_2025_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7254a50abcedd23054484ba5 | questions:bank_2025_2_1_q25 | location_pending | Human must verify evidence location | {} |
| audit-4d416e08b1365dde266653b9 | questions:bank_2025_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-136ce9151c2398a3e345df90 | questions:bank_2025_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e11d133458e4204f200c2f04 | questions:bank_2025_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ce5bf0488824add21ec85ea1 | questions:bank_2025_2_2_q28 | location_pending | Human must verify evidence location | {} |
| audit-3b7da4399c953f2e1324bebe | questions:bank_2025_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f2c14d5807926d97d76692fc | questions:bank_2025_2_2_q29 | location_pending | Human must verify evidence location | {} |
| audit-7798a9d4c8ae6fe1a0ce8620 | questions:bank_2025_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-7bd1b3ebbf5920847d5b5596 | questions:bank_2025_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-fef6bb6e68254194cb735cfd | questions:bank_2025_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3020a7098dba616f467c4b44 | questions:bank_2025_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c9663199d0d242647e141519 | questions:bank_2025_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-c9dbb03cc7af98c613c23ca4 | questions:bank_2025_2_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-024013843f665bdc3727e427 | questions:bank_2025_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2f746ceaf957b8d9353cca3c | questions:bank_2025_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-82e4ec77cb88d4fe8009a963 | questions:bank_2025_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a51bcb7ef59ef0871205a379 | questions:bank_2025_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-99a0823956a8f41d0130bee7 | questions:bank_2025_2_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-c6473ec63371067c33d6b7bb | questions:bank_2025_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-49030b3be2601499eff69eba | questions:bank_2025_2_4_q39 | location_pending | Human must verify evidence location | {} |
| audit-a2efbea4713e88f7af0212e6 | questions:bank_2025_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d414089d1a80c8cee2c0822f | questions:bank_2025_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-c2c4ca1700e89b56d8397fbf | questions:bank_2025_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-08bcb1cecd7d8709752d5979 | questions:bank_2026_1_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-23da19770b7212cd4f3588cf | questions:bank_2026_1_1_q22 | location_pending | Human must verify evidence location | {} |
| audit-560143c249f47212a7a50c92 | questions:bank_2026_1_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-eb649757e1f866a4d98a0f69 | questions:bank_2026_1_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b50d269538fbf1b066cad3c8 | questions:bank_2026_1_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-b924cd173661305a0ba03b88 | questions:bank_2026_1_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d25868feceff55510c8c12b3 | questions:bank_2026_1_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-ac593182019bb00c740bb3cd | questions:bank_2026_1_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-527e3ef23f165903926db6d8 | questions:bank_2026_1_2_q27 | location_pending | Human must verify evidence location | {} |
| audit-66c3a8d546d48a143a374bf2 | questions:bank_2026_1_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4ab827afbefe15870c401055 | questions:bank_2026_1_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-0976c46bfca004a198d583f8 | questions:bank_2026_1_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-04c54e13cd6f2c93dcf4b5ff | questions:bank_2026_1_2_q30 | location_pending | Human must verify evidence location | {} |
| audit-1788494f4b12bf06694d89ed | questions:bank_2026_1_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-a9bb0f3ee793b372b2916af2 | questions:bank_2026_1_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dbd273153003c4d130dc723a | questions:bank_2026_1_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-3edec3f51ada2d06724ba1a4 | questions:bank_2026_1_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-053045b89622f2b877cae750 | questions:bank_2026_1_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-21b84d44cc054b32e5b5b664 | questions:bank_2026_1_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-9b7d879ed8f2fd494917f519 | questions:bank_2026_1_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-4c0621ee2fdb90194dce52ef | questions:bank_2026_1_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-32ec67eaa59216a711fe981b | questions:bank_2026_1_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-34ef34f784613ce045457626 | questions:bank_2026_1_4_q38 | location_pending | Human must verify evidence location | {} |
| audit-17a32a9a8833c3e6bc275214 | questions:bank_2026_1_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-cbb550201bd33990364a749f | questions:bank_2026_1_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b73deedb06bc2d259953508f | questions:bank_2026_1_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-566ea80bd7110cbdace9d682 | questions:bank_2026_1_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-b9b93f462755d435790b8679 | questions:bank_2026_2_1_q21 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e4880660854a7ce7370d3a15 | questions:bank_2026_2_1_q22 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-9728a1232f22f51534c2958d | questions:bank_2026_2_1_q23 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-dec2a53478241ad22615979d | questions:bank_2026_2_1_q24 | location_pending | Human must verify evidence location | {} |
| audit-3072a33a7b600f8d6c8dc86a | questions:bank_2026_2_1_q24 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-940c46e09626862bf855af5f | questions:bank_2026_2_1_q25 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1b58d98dcccaea9cf4002fa5 | questions:bank_2026_2_2_q26 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-1ad9c8399a391bdafb276195 | questions:bank_2026_2_2_q27 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-f693015c8a5e6034d01793b0 | questions:bank_2026_2_2_q28 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-6811658dd54e113c86e0fe45 | questions:bank_2026_2_2_q29 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-910f3cb6b01a46da6eb2815e | questions:bank_2026_2_2_q30 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-471e77bf6aac61e13c31432a | questions:bank_2026_2_3_q31 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e64a8881abeaec916a0c35b8 | questions:bank_2026_2_3_q32 | location_pending | Human must verify evidence location | {} |
| audit-cbe8e381f142853a98f6126a | questions:bank_2026_2_3_q32 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e5c4722c895ff88336381d2e | questions:bank_2026_2_3_q33 | location_pending | Human must verify evidence location | {} |
| audit-3ace4c3b2bac3df1ba0811ce | questions:bank_2026_2_3_q33 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-6f591972654512e5a2e25910 | questions:bank_2026_2_3_q34 | location_pending | Human must verify evidence location | {} |
| audit-27a091ba95f515d130bdcb74 | questions:bank_2026_2_3_q34 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-186013b2f59a3f227ee5af50 | questions:bank_2026_2_3_q35 | location_pending | Human must verify evidence location | {} |
| audit-7c74b4cfba9bd536f0c0358f | questions:bank_2026_2_3_q35 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2de93e073663c89e69ea64de | questions:bank_2026_2_4_q36 | location_pending | Human must verify evidence location | {} |
| audit-fee4d6e33eb226552e92d423 | questions:bank_2026_2_4_q36 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-cf72792f77aadbca9e70dd60 | questions:bank_2026_2_4_q37 | location_pending | Human must verify evidence location | {} |
| audit-23449ad5d9d5d7d9e9816d45 | questions:bank_2026_2_4_q37 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-2c0f7ccb519264ec3f567013 | questions:bank_2026_2_4_q38 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e817f36fd0731fd2640ba4ce | questions:bank_2026_2_4_q39 | location_pending | Human must verify evidence location | {} |
| audit-f820c673e2291b267d58ef55 | questions:bank_2026_2_4_q39 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-e6d899aa478a88448b8d531f | questions:bank_2026_2_4_q40 | location_pending | Human must verify evidence location | {} |
| audit-cb4dee57175e35c1bddf1786 | questions:bank_2026_2_4_q40 | question_content_review | Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified | {} |
| audit-d89609aa7d47dfda94261cd6 | sentences:auto_8afe3a8d_s4 | offset_unverified | Sentence offsets require human verification | {} |

