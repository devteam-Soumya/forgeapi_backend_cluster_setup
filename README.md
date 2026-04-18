# ⚡ ForgeAPI

AI-powered backend scaffolding for generating FastAPI + MongoDB modules with support for:

- public APIs
- authenticated APIs
- RBAC-protected APIs
- tenant-aware database selection
- separate public and secure app entrypoints

---

## 📦 Installation

```bash
git clone https://github.com/devteam-Soumya/Forgeapi_Backend_Development.git
cd Forgeapi_Backend_Development
pip install -e .
⚙️ Environment Setup
Create a .env file in your project root:
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=forgeapi
ANTHROPIC_API_KEY=your_api_key_here
🚀 Quick Start
1. Generate a module
Public API only
forgeapi create --module-name product --tenant-id 890 --database-mode same --access public --field name:str:true:false --field description:str:false:false --field price:float:true:false --field inStock:bool:true:false --field category:str:false:false
Secure API only (RBAC)
forgeapi create --module-name category --tenant-id 890 --database-mode same --access rbac --field name:str:true:false --field slug:str:true:true --field isActive:bool:true:false
Public + Secure API for same module
forgeapi create --module-name product --tenant-id 890 --database-mode same --access public --access rbac --field name:str:true:false --field description:str:false:false --field price:float:true:false --field inStock:bool:true:false --field category:str:false:false
Using a different database
forgeapi create --module-name supplier --tenant-id 890 --database-mode different --database-name tenant_890_supplier_db --access auth --field name:str:true:false --field contactEmail:str:false:false --field phone:str:false:false

# 2. Start the API(public)
cd generated/backend
uvicorn main_public:app --reload --port 8000
2.1 Start the API(private)
cd generated/backend
uvicorn main_secure:app --reload --port 8000

# 3. Open docs
# http://localhost:8000/docs
🧩 CLI Options
forgeapi create
Option	Description
--module-name	Name of the resource, for example product
--tenant-id	Tenant identifier used for DB resolution
--database-mode	same or different
--database-name	Required when --database-mode different
--access	public | auth | rbac (repeatable)
--field	name:type:required:unique (repeatable)
Field format
name:type:required:unique
Example
name      → field name (camelCase or snake_case)
type      → str | int | float | bool | datetime
required  → true | false
unique    → true | false  (creates a MongoDB unique index)
🏗️ Access Modes
public
no authentication required
auth
bearer token required
rbac
bearer token required
permission required

You can repeat --access to generate both public and secure variants for the same module.
Example:
forgeapi create --module-name order --tenant-id 890 --database-mode same --access public --access rbac --field orderNumber:str:true:true --field total:float:true:false --field status:str:true:false
🗄️ Database Selection

ForgeAPI supports tenant-aware DB resolution.

--database-mode same

Uses the default DB derived for the tenant.

Example:

tenant 890 → tenant_890_db
tenant 901 → tenant_901_db
--database-mode different

Uses a custom DB name provided explicitly.
Example:
--database-mode different --database-name tenant_890_orders_db
Important
one generation flow uses one resolved database
changing tenant does not delete the old DB
each tenant can map to its own DB
custom DBs can also be used when required
🍃 MongoDB Behavior

Collections are created automatically on first insert/request inside the resolved database.

Example resolved database:
tenant_890_db
Possible collections:
products
categories
customers
orders
inventories
payments
reviews
suppliers
users
If unique: true is used for a field, ForgeAPI metadata will mark it as unique.
If your runtime layer implements index creation, that field should get a MongoDB unique index.
🌐 Generated API Endpoints

Each generated module exposes standard CRUD-style endpoints.

Public app (main.py)

If module has public access:

POST /{module}s/
GET /{module}s/
GET /{module}s/{id}
Secure app (main_secure.py)

If module has auth or rbac access:

POST /{module}s/
GET /{module}s/
GET /{module}s/{id}
Auth endpoints

Available only in main_secure.py:

POST /auth/signup
POST /auth/login
📁 Project Structure
Forgeapi_Backend_Development/
├── mini_agent/
│   ├── cli.py
│   ├── orchestrator.py
│   ├── backend_codegen_agent.py
│   ├── spec.py
│   ├── template_engine.py
│   ├── validator_agent.py
│   ├── registry.py
│   ├── database_resolver.py
│   ├── llm.py
│   └── fixer.py
├── generated/
│   └── backend/
│       ├── auth/
│       ├── product/
│       │   ├── __init__.py
│       │   ├── schemas.py
│       │   ├── crud.py
│       │   ├── router_public.py
│       │   ├── router_secure.py
│       │   └── metadata.json
│       ├── main.py
│       └── main_secure.py
├── setup.py
├── requirements.txt
└── .env
📌 Example Create Commands
forgeapi create --module-name product --tenant-id 890 --database-mode same --access public --access rbac --field name:str:true:false --field description:str:false:false --field price:float:true:false --field inStock:bool:true:false --field category:str:false:false

forgeapi create --module-name category --tenant-id 890 --database-mode same --access public --access rbac --field name:str:true:false --field slug:str:true:true --field isActive:bool:true:false

forgeapi create --module-name customer --tenant-id 890 --database-mode same --access public --access auth --field name:str:true:false --field email:str:true:true

forgeapi create --module-name order --tenant-id 890 --database-mode same --access public --access rbac --field orderNumber:str:true:true --field total:float:true:false --field status:str:true:false

forgeapi create --module-name inventory --tenant-id 890 --database-mode same --access auth --field sku:str:true:true --field quantity:int:true:false

forgeapi create --module-name payment --tenant-id 890 --database-mode same --access rbac --field transactionId:str:true:true --field amount:float:true:false --field status:str:true:false

forgeapi create --module-name review --tenant-id 890 --database-mode same --access public --field comment:str:true:false --field rating:int:true:false

forgeapi create --module-name supplier --tenant-id 890 --database-mode different --database-name tenant_890_supplier_db --access auth --field name:str:true:false --field contactEmail:str:false:false --field phone:str:false:false
✅ Example Workflow
Generate module
forgeapi create --module-name customer --tenant-id 890 --database-mode same --access auth --field name:str:true:false --field email:str:true:true
Run secure app
cd generated/backend
uvicorn main_secure:app --reload --port 8000
Signup

Use:

POST /auth/signup
Login

Use:

POST /auth/login
Test generated endpoints

Example:

POST /customers/
GET /customers/
GET /customers/{id}

Pass:

Authorization: Bearer <token> for secure endpoints
x-tenant-id: 890
📋 Requirements
fastapi
uvicorn
pymongo
pydantic
python-dotenv
pytest
httpx
requests
bcrypt
pyjwt
Install dependencies:
pip install -r requirements.txt
📄 License

MIT

Main changes from your old README:

- removed the old fixed single-DB-only explanation
- added `--tenant-id`
- added `--database-mode`
- added `--database-name`
- clarified `main.py` = public only
- clarified `main_secure.py` = auth + secure only
- removed `main_public.py`
- updated structure from `router.py/service.py` to `router_public.py`, `router_secure.py`, `crud.py`
- updated examples for tenant-aware DB resolution
- kept it **without MongoDB cluster wording**, as you asked

If you want, I can also give you a shorter, cleaner README version for GitHub that is more polished and less implementation-heavy.
