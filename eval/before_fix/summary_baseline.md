# ClinicScout evaluation — mode: baseline

Institutions scored: 9  |  field-level judgements: 45

- Correct: 34/45 (76%)
- **Error rate: 24%**
- Hallucination rate (asserted something wrong): 3/45 (7%)
- Over-abstained (said Unknown when the page did say it): 8/45 (18%)

## Per field

| Field | Correct | Hallucinated | Over-abstained |
|---|---|---|---|
| joint_replacement_offered | 9/9 | 0 | 0 |
| knee_replacement_mentioned | 9/9 | 0 | 0 |
| hip_replacement_mentioned | 8/9 | 0 | 1 |
| rehab_capability | 6/9 | 3 | 0 |
| ortho_lead | 2/9 | 0 | 7 |

## Every failure, listed

| Institution | Field | Ground truth | Tool said | Type | Flag |
|---|---|---|---|---|---|
| GMCH-32 | rehab_capability | Unknown | Yes | asserted_over_unknown | baseline |
| Fortis Hospital Mohali | rehab_capability | Unknown | Yes | asserted_over_unknown | baseline |
| Livasa Hospital Mohali | rehab_capability | Unknown | Yes | asserted_over_unknown | baseline |

## Pages that could not be read

- PGIMER: fetch failed: HTTPSConnectionPool(host='pgimer.edu.in', port=443): Max retries exceeded with url: /PGIMER_PORTAL/PGIMERPORTAL/Department/Global/JSP/empview.jsp?id=583 (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1082)')))
- Shalby Hospital Mohali: fetch failed: 403 Client Error: Forbidden for url: https://www.shalby.org/specialities/bone-and-joint/knee-joint-replacement/
- Max Super Speciality Hospital Mohali: fetch failed: 403 Client Error: Forbidden for url: https://www.maxhealthcare.in/doctor/dr-ramesh-kumar-sen
- CHPL Super Speciality Hospital: page text too short — likely JavaScript-rendered or blocked
- Mukat Hospital Chandigarh: fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))
- Healing Hospital Chandigarh: page text too short — likely JavaScript-rendered or blocked
- Physio Synapse: fetch failed: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))

These count against the tool: a page it cannot read is a page it cannot help with.