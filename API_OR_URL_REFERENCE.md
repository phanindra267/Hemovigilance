# RedLink URL & Module Reference

| Module | URL Route | View Name | Allowed Roles | Description |
|---|---|---|---|---|
| **Core** | / | core:home | Public | Landing page & compatibility chart |
| **Core** | /about/ | core:about | Public | System overview & domain principles |
| **Core** | /guidelines/ | core:guidelines | Public | SOP regulatory parameters |
| **Accounts** | /accounts/login/ | ccounts:login | Public | User authentication |
| **Accounts** | /accounts/logout/ | ccounts:logout | Authenticated | User logout & audit log |
| **Accounts** | /accounts/dashboard/ | ccounts:dashboard | Authenticated | Role-tailored dashboard |
| **Accounts** | /accounts/register/donor/ | ccounts:register_donor | Public | Donor self-registration |
| **Accounts** | /accounts/register/hospital/ | ccounts:register_hospital | Public | Hospital representative registration |
| **Accounts** | /accounts/profile/ | ccounts:profile | Authenticated | Profile details & contact update |
| **Accounts** | /accounts/users/ | ccounts:user_list | Super Admin, BB Admin | System users & staff directory |
| **Donors** | /donors/ | donors:list | Staff, Admins | Donor database & search |
| **Donors** | /donors/create/ | donors:create | Staff, Admins | Register new blood donor |
| **Donors** | /donors/<pk>/ | donors:detail | Authenticated | Donor profile & donation history |
| **Donors** | /donors/<pk>/assessment/ | donors:assess_eligibility | Medical Officer, Admin | Medical eligibility assessment |
| **Appointments** | /appointments/ | ppointments:list | Authenticated | Appointments calendar & list |
| **Appointments** | /appointments/create/ | ppointments:create | Authenticated | Schedule donation appointment |
| **Appointments** | /appointments/<pk>/checkin/ | ppointments:checkin | Staff, Admins | Check-in donor for collection |
| **Camps** | /camps/ | camps:list | Authenticated | Blood donation drives list |
| **Camps** | /camps/create/ | camps:create | Staff, Admins | Organize community/corporate camp |
| **Donations** | /donations/ | donations:list | Staff, Admins | Phlebotomy sessions list |
| **Donations** | /donations/create/ | donations:create | Staff, Admins | Record blood collection |
| **Laboratory** | /laboratory/bags/ | laboratory:blood_bag_list | Staff, Admins | Blood bags inventory & status |
| **Laboratory** | /laboratory/samples/ | laboratory:sample_list | Lab Tech, MO, Admin | Laboratory screening queue |
| **Laboratory** | /laboratory/samples/<pk>/verify/| laboratory:verify_sample | Medical Officer, Admin | Medical officer verification & release |
| **Components** | /components/ | lood_components:list | Staff, Admins | Component inventory list |
| **Components** | /components/separate/<pk>/ | lood_components:separate| Tech, MO, Admin | Fractionation & component preparation |
| **Inventory** | /inventory/ | inventory:stock | Staff, Admins | Physical inventory & cold storage |
| **Inventory** | /inventory/<pk>/quarantine/ | inventory:quarantine | Staff, Admins | Place unit in quarantine |
| **Inventory** | /inventory/<pk>/release/ | inventory:release | Medical Officer, Admin | Release unit from quarantine |
| **Requests** | /requests/ | 
equests_app:list | Authenticated | Hospital blood requisitions |
| **Requests** | /requests/create/ | 
equests_app:create | Authenticated | Submit new blood order |
| **Requests** | /requests/<pk>/review/ | 
equests_app:review | Medical Officer, Admin | Approve or reject requisition |
| **Requests** | /requests/reserve/<pk>/ | 
equests_app:reserve_inventory| Tech, MO, Admin | Atomic unit reservation |
| **Requests** | /requests/reservation/<pk>/issue/| 
equests_app:issue_blood| Tech, MO, Admin | Issue blood unit to hospital |
| **Requests** | /requests/issue/<pk>/return/ | 
equests_app:return_blood | Tech, MO, Admin | Record blood return & clinical triage |
| **Requests** | /requests/inventory/<pk>/discard/| 
equests_app:discard_unit| Tech, MO, Admin | Authorize biohazard discard |
| **Reports** | /reports/ | 
eports:index | Staff, Admins | Operational reports hub |
| **Reports** | /reports/donors/ | 
eports:donors | Staff, Admins | Donor report (CSV/PDF) |
| **Reports** | /reports/inventory/ | 
eports:inventory | Staff, Admins | Inventory report (CSV/PDF) |
| **Reports** | /reports/issues/ | 
eports:issues | Staff, Admins | Distribution report (CSV/PDF) |
| **Reports** | /reports/discards/ | 
eports:discards | Staff, Admins | Discard report (CSV/PDF) |
| **Audit** | /audit/ | udit:list | Super Admin, BB Admin, MO | Regulatory audit trail |
