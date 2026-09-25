# ClinicScout evaluation — mode: llm

Institutions scored: 20  |  field-level judgements: 100

- Correct: 35/100 (35%)
- **Error rate: 65%**
- Hallucination rate (asserted something wrong): 3/100 (3%)
- Over-abstained (said Unknown when the page did say it): 7/100 (7%)
- Unreadable or missing page: 55/100 (55%)

## Per field

| Field | Correct | Hallucinated | Over-abstained | Unreadable |
|---|---|---|---|---|
| joint_replacement_offered | 9/20 | 0 | 0 | 11 |
| knee_replacement_mentioned | 8/20 | 0 | 1 | 11 |
| hip_replacement_mentioned | 6/20 | 0 | 3 | 11 |
| rehab_capability | 4/20 | 2 | 3 | 11 |
| ortho_lead | 8/20 | 1 | 0 | 11 |

## Every failure, listed

| Institution | Field | Ground truth | Tool said | Type | Flag |
|---|---|---|---|---|---|
| PGIMER | joint_replacement_offered | Unknown | Unknown | page_unreadable | no cached page |
| PGIMER | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| PGIMER | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| PGIMER | rehab_capability | Unknown | Unknown | page_unreadable | no cached page |
| PGIMER | ortho_lead | Prof. Aditya K. Aggarwal | Unknown | page_unreadable | no cached page |
| Fortis Hospital Mohali | rehab_capability | Unknown | Yes | asserted_over_unknown |  |
| Shalby Hospital Mohali | joint_replacement_offered | Yes | Unknown | page_unreadable | no cached page |
| Shalby Hospital Mohali | knee_replacement_mentioned | Yes | Unknown | page_unreadable | no cached page |
| Shalby Hospital Mohali | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Shalby Hospital Mohali | rehab_capability | Unknown | Unknown | page_unreadable | no cached page |
| Shalby Hospital Mohali | ortho_lead | Dr. Gurdarshan Singh Natt | Unknown | page_unreadable | no cached page |
| Park Grecian Super Speciality Hospital Mohali | knee_replacement_mentioned | Yes | Unknown | missed |  |
| Park Grecian Super Speciality Hospital Mohali | hip_replacement_mentioned | Yes | Unknown | missed |  |
| Park Grecian Super Speciality Hospital Mohali | rehab_capability | Yes | Unknown | missed |  |
| Livasa Hospital Mohali | rehab_capability | Unknown | Yes | asserted_over_unknown |  |
| Max Super Speciality Hospital Mohali | joint_replacement_offered | Yes | Unknown | page_unreadable | no cached page |
| Max Super Speciality Hospital Mohali | knee_replacement_mentioned | Yes | Unknown | page_unreadable | no cached page |
| Max Super Speciality Hospital Mohali | hip_replacement_mentioned | Yes | Unknown | page_unreadable | no cached page |
| Max Super Speciality Hospital Mohali | rehab_capability | Unknown | Unknown | page_unreadable | no cached page |
| Max Super Speciality Hospital Mohali | ortho_lead | Dr. Ramesh Kumar Sen | Unknown | page_unreadable | no cached page |
| CHPL Super Speciality Hospital | joint_replacement_offered | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | knee_replacement_mentioned | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | rehab_capability | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | ortho_lead | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Ojas Hospital Panchkula | hip_replacement_mentioned | Yes | Unknown | missed |  |
| Ojas Hospital Panchkula | rehab_capability | Yes | Unknown | missed | no_rehab_term_in_evidence |
| Paras Health Panchkula | ortho_lead | Dr. Jagandeep Virk | Dr. Ravi Kumar Gupta | wrong_name |  |
| Park Hospital Panchkula | hip_replacement_mentioned | Yes | Unknown | missed |  |
| Mukat Hospital Chandigarh | joint_replacement_offered | Yes | Unknown | page_unreadable | no cached page |
| Mukat Hospital Chandigarh | knee_replacement_mentioned | Yes | Unknown | page_unreadable | no cached page |
| Mukat Hospital Chandigarh | hip_replacement_mentioned | Yes | Unknown | page_unreadable | no cached page |
| Mukat Hospital Chandigarh | rehab_capability | Yes | Unknown | page_unreadable | no cached page |
| Mukat Hospital Chandigarh | ortho_lead | Dr. Sumu Chowdhury | Unknown | page_unreadable | no cached page |
| Healing Hospital Chandigarh | joint_replacement_offered | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | knee_replacement_mentioned | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | hip_replacement_mentioned | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | rehab_capability | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | ortho_lead | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Command Hospital Western Command Chandimandir | joint_replacement_offered | Unknown | Unknown | page_unreadable | no cached page |
| Command Hospital Western Command Chandimandir | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Command Hospital Western Command Chandimandir | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Command Hospital Western Command Chandimandir | rehab_capability | Unknown | Unknown | page_unreadable | no cached page |
| Command Hospital Western Command Chandimandir | ortho_lead | Unknown | Unknown | page_unreadable | no cached page |
| GMSH-16 | joint_replacement_offered | Unknown | Unknown | page_unreadable | no cached page |
| GMSH-16 | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| GMSH-16 | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| GMSH-16 | rehab_capability | Unknown | Unknown | page_unreadable | no cached page |
| GMSH-16 | ortho_lead | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Mohali | joint_replacement_offered | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Mohali | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Mohali | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Mohali | rehab_capability | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Mohali | ortho_lead | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Sector 6 Panchkula | joint_replacement_offered | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Sector 6 Panchkula | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Sector 6 Panchkula | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Sector 6 Panchkula | rehab_capability | Unknown | Unknown | page_unreadable | no cached page |
| Civil Hospital Sector 6 Panchkula | ortho_lead | Unknown | Unknown | page_unreadable | no cached page |
| Physio Synapse | joint_replacement_offered | No | Unknown | page_unreadable | no cached page |
| Physio Synapse | knee_replacement_mentioned | Yes | Unknown | page_unreadable | no cached page |
| Physio Synapse | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no cached page |
| Physio Synapse | rehab_capability | Yes | Unknown | page_unreadable | no cached page |
| Physio Synapse | ortho_lead | Unknown | Unknown | page_unreadable | no cached page |
| Independent home-visit physiotherapy provider | rehab_capability | Yes | Unknown | missed | no_rehab_term_in_evidence |

## Pages that could not be read

- PGIMER: no cached page
- Shalby Hospital Mohali: no cached page
- Max Super Speciality Hospital Mohali: no cached page
- CHPL Super Speciality Hospital: page text too short — likely JavaScript-rendered or blocked
- Mukat Hospital Chandigarh: no cached page
- Healing Hospital Chandigarh: page text too short — likely JavaScript-rendered or blocked
- Command Hospital Western Command Chandimandir: no cached page
- GMSH-16: no cached page
- Civil Hospital Mohali: no cached page
- Civil Hospital Sector 6 Panchkula: no cached page
- Physio Synapse: no cached page

Each unreadable or missing page contributes five errors: a page the tool cannot read is a page it cannot help with.