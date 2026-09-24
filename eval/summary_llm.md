# ClinicScout evaluation — mode: llm

Institutions scored: 20  |  field-level judgements: 100

- Correct: 35/100 (35%)
- **Error rate: 65%**
- Hallucination rate (asserted something wrong): 4/100 (4%)
- Over-abstained (said Unknown when the page did say it): 6/100 (6%)
- Unreadable or missing page: 55/100 (55%)

## Per field

| Field | Correct | Hallucinated | Over-abstained | Unreadable |
|---|---|---|---|---|
| joint_replacement_offered | 9/20 | 0 | 0 | 11 |
| knee_replacement_mentioned | 8/20 | 0 | 1 | 11 |
| hip_replacement_mentioned | 6/20 | 0 | 3 | 11 |
| rehab_capability | 4/20 | 3 | 2 | 11 |
| ortho_lead | 8/20 | 1 | 0 | 11 |

## Every failure, listed

| Institution | Field | Ground truth | Tool said | Type | Flag |
|---|---|---|---|---|---|
| PGIMER | joint_replacement_offered | Unknown | Unknown | page_unreadable | fetch failed: HTTPSConnectionPool(host='pgimer.edu.in', port=443): Max retries exceeded with url: /PGIMER_PORTAL/PGIMERPORTAL/Department/Global/JSP/empview.jsp?id=583 (Caused by SSLError(SSLCertVerifi |
| PGIMER | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | fetch failed: HTTPSConnectionPool(host='pgimer.edu.in', port=443): Max retries exceeded with url: /PGIMER_PORTAL/PGIMERPORTAL/Department/Global/JSP/empview.jsp?id=583 (Caused by SSLError(SSLCertVerifi |
| PGIMER | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | fetch failed: HTTPSConnectionPool(host='pgimer.edu.in', port=443): Max retries exceeded with url: /PGIMER_PORTAL/PGIMERPORTAL/Department/Global/JSP/empview.jsp?id=583 (Caused by SSLError(SSLCertVerifi |
| PGIMER | rehab_capability | Unknown | Unknown | page_unreadable | fetch failed: HTTPSConnectionPool(host='pgimer.edu.in', port=443): Max retries exceeded with url: /PGIMER_PORTAL/PGIMERPORTAL/Department/Global/JSP/empview.jsp?id=583 (Caused by SSLError(SSLCertVerifi |
| PGIMER | ortho_lead | Prof. Aditya K. Aggarwal | Unknown | page_unreadable | fetch failed: HTTPSConnectionPool(host='pgimer.edu.in', port=443): Max retries exceeded with url: /PGIMER_PORTAL/PGIMERPORTAL/Department/Global/JSP/empview.jsp?id=583 (Caused by SSLError(SSLCertVerifi |
| GMCH-32 | rehab_capability | Unknown | Yes | asserted_over_unknown |  |
| Fortis Hospital Mohali | rehab_capability | Unknown | Yes | asserted_over_unknown |  |
| Shalby Hospital Mohali | joint_replacement_offered | Yes | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.shalby.org/specialities/bone-and-joint/knee-joint-replacement/ |
| Shalby Hospital Mohali | knee_replacement_mentioned | Yes | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.shalby.org/specialities/bone-and-joint/knee-joint-replacement/ |
| Shalby Hospital Mohali | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.shalby.org/specialities/bone-and-joint/knee-joint-replacement/ |
| Shalby Hospital Mohali | rehab_capability | Unknown | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.shalby.org/specialities/bone-and-joint/knee-joint-replacement/ |
| Shalby Hospital Mohali | ortho_lead | Dr. Gurdarshan Singh Natt | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.shalby.org/specialities/bone-and-joint/knee-joint-replacement/ |
| Park Grecian Super Speciality Hospital Mohali | knee_replacement_mentioned | Yes | Unknown | missed |  |
| Park Grecian Super Speciality Hospital Mohali | hip_replacement_mentioned | Yes | Unknown | missed |  |
| Livasa Hospital Mohali | rehab_capability | Unknown | Yes | asserted_over_unknown |  |
| Max Super Speciality Hospital Mohali | joint_replacement_offered | Yes | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.maxhealthcare.in/doctor/dr-ramesh-kumar-sen |
| Max Super Speciality Hospital Mohali | knee_replacement_mentioned | Yes | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.maxhealthcare.in/doctor/dr-ramesh-kumar-sen |
| Max Super Speciality Hospital Mohali | hip_replacement_mentioned | Yes | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.maxhealthcare.in/doctor/dr-ramesh-kumar-sen |
| Max Super Speciality Hospital Mohali | rehab_capability | Unknown | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.maxhealthcare.in/doctor/dr-ramesh-kumar-sen |
| Max Super Speciality Hospital Mohali | ortho_lead | Dr. Ramesh Kumar Sen | Unknown | page_unreadable | fetch failed: 403 Client Error: Forbidden for url: https://www.maxhealthcare.in/doctor/dr-ramesh-kumar-sen |
| CHPL Super Speciality Hospital | joint_replacement_offered | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | knee_replacement_mentioned | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | rehab_capability | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| CHPL Super Speciality Hospital | ortho_lead | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Ojas Hospital Panchkula | hip_replacement_mentioned | Yes | Unknown | missed |  |
| Ojas Hospital Panchkula | rehab_capability | Yes | Unknown | missed | no_rehab_term_in_evidence |
| Paras Health Panchkula | ortho_lead | Dr. Jagandeep Virk | Dr. Ravi Kumar Gupta | wrong_name |  |
| Park Hospital Panchkula | hip_replacement_mentioned | Yes | Unknown | missed |  |
| Mukat Hospital Chandigarh | joint_replacement_offered | Yes | Unknown | page_unreadable | fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer')) |
| Mukat Hospital Chandigarh | knee_replacement_mentioned | Yes | Unknown | page_unreadable | fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer')) |
| Mukat Hospital Chandigarh | hip_replacement_mentioned | Yes | Unknown | page_unreadable | fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer')) |
| Mukat Hospital Chandigarh | rehab_capability | Yes | Unknown | page_unreadable | fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer')) |
| Mukat Hospital Chandigarh | ortho_lead | Dr. Sumu Chowdhury | Unknown | page_unreadable | fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer')) |
| Healing Hospital Chandigarh | joint_replacement_offered | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | knee_replacement_mentioned | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | hip_replacement_mentioned | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | rehab_capability | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Healing Hospital Chandigarh | ortho_lead | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Command Hospital Western Command Chandimandir | joint_replacement_offered | Unknown | Unknown | page_unreadable | no official page found |
| Command Hospital Western Command Chandimandir | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| Command Hospital Western Command Chandimandir | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| Command Hospital Western Command Chandimandir | rehab_capability | Unknown | Unknown | page_unreadable | no official page found |
| Command Hospital Western Command Chandimandir | ortho_lead | Unknown | Unknown | page_unreadable | no official page found |
| GMSH-16 | joint_replacement_offered | Unknown | Unknown | page_unreadable | no official page found |
| GMSH-16 | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| GMSH-16 | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| GMSH-16 | rehab_capability | Unknown | Unknown | page_unreadable | no official page found |
| GMSH-16 | ortho_lead | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Mohali | joint_replacement_offered | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Mohali | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Mohali | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Mohali | rehab_capability | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Mohali | ortho_lead | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Sector 6 Panchkula | joint_replacement_offered | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Sector 6 Panchkula | knee_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Sector 6 Panchkula | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Sector 6 Panchkula | rehab_capability | Unknown | Unknown | page_unreadable | no official page found |
| Civil Hospital Sector 6 Panchkula | ortho_lead | Unknown | Unknown | page_unreadable | no official page found |
| Physio Synapse | joint_replacement_offered | No | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Physio Synapse | knee_replacement_mentioned | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Physio Synapse | hip_replacement_mentioned | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Physio Synapse | rehab_capability | Yes | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Physio Synapse | ortho_lead | Unknown | Unknown | page_unreadable | page text too short — likely JavaScript-rendered or blocked |
| Independent home-visit physiotherapy provider | rehab_capability | Yes | Unknown | missed | no_rehab_term_in_evidence |

## Pages that could not be read

- PGIMER: fetch failed: HTTPSConnectionPool(host='pgimer.edu.in', port=443): Max retries exceeded with url: /PGIMER_PORTAL/PGIMERPORTAL/Department/Global/JSP/empview.jsp?id=583 (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1082)')))
- Shalby Hospital Mohali: fetch failed: 403 Client Error: Forbidden for url: https://www.shalby.org/specialities/bone-and-joint/knee-joint-replacement/
- Max Super Speciality Hospital Mohali: fetch failed: 403 Client Error: Forbidden for url: https://www.maxhealthcare.in/doctor/dr-ramesh-kumar-sen
- CHPL Super Speciality Hospital: page text too short — likely JavaScript-rendered or blocked
- Mukat Hospital Chandigarh: fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))
- Healing Hospital Chandigarh: page text too short — likely JavaScript-rendered or blocked
- Command Hospital Western Command Chandimandir: no official page found
- GMSH-16: no official page found
- Civil Hospital Mohali: no official page found
- Civil Hospital Sector 6 Panchkula: no official page found
- Physio Synapse: page text too short — likely JavaScript-rendered or blocked

Each unreadable or missing page contributes five errors: a page the tool cannot read is a page it cannot help with.