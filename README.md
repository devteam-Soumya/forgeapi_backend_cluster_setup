⚡ ForgeAPI

AI-powered backend scaffolding — generate production-ready FastAPI + MongoDB modules with a single command.
📦 Installation
git clone https://github.com/devteam-Soumya/Forgeapi_Backend_Development.git
cd Forgeapi_Backend_Development
pip install -e .
⚙️ Environment Setup
Create a .env file in your project root:
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=forgeapi
ANTHROPIC_API_KEY=your_api_key_here
🚀 Quick Start
# 1. Generate a module
public API Creation:
forgeapi create --module-name product --access public --field name:str:true:false --field description:str:false:false --field price:float:true:false --field inStock:bool:true:false --field category:str:false:false
private API Creation:
forgeapi create --module-name product --access public --access rbac --field name:str:true:false --field description:str:false:false --field price:float:true:false --field inStock:bool:true:false --field category:str:false:false
# 2. Start the API(public)
cd generated/backend
uvicorn main_public:app --reload --port 8000
2.1 Start the API(private)
cd generated/backend
uvicorn main_secure:app --reload --port 8000

# 3. Open docs
# http://localhost:8000/docs
create options
--module-name   Name of the resource (e.g. product)
--access        public | auth | rbac  (repeatable)
--field         name:type:required:unique  (repeatable)
Field format
name:type:required:unique

name      → field name (camelCase or snake_case)
type      → str | int | float | bool | datetime
required  → true | false
unique    → true | false  (creates a MongoDB unique index)
📁 Project Structure
Forgeapi_Backend_Development/
├── mini_agent/
│   ├── cli.py                  # CLI entry point
│   ├── orchestrator.py         # Module lifecycle
│   ├── backend_codegen_agent.py# AI code generation
│   ├── spec.py                 # Module spec builder
│   ├── template_engine.py      # Jinja2 templates
│   ├── validator_agent.py      # Code validation
│   ├── registry.py             # Module registry
│   ├── llm.py                  # Anthropic API client
│   └── fixer.py                # Auto-repair generated code
├── generated/
│   └── backend/
│       ├── auth/
│       ├── product/
│       │   ├── __init__.py
│       │   ├── router.py       # FastAPI routes
│       │   ├── schemas.py      # Pydantic models
│       │   ├── service.py      # DB operations
│       │   └── metadata.json
│       └── main.py
├── setup.py
├── requirements.txt
└── .env
<details>
<summary>View all create commands</summary>

forgeapi create --module-name product --access public --access rbac \
  --field name:str:true:false --field description:str:false:false \
  --field price:float:true:false --field inStock:bool:true:false \
  --field category:str:false:false

forgeapi create --module-name category --access rbac \
  --field name:str:true:false --field slug:str:true:true \
  --field isActive:bool:true:false

forgeapi create --module-name customer --access public --access auth \
  --field name:str:true:false --field email:str:true:true

forgeapi create --module-name order --access public --access rbac \
  --field orderNumber:str:true:true --field total:float:true:false \
  --field status:str:true:false

forgeapi create --module-name inventory --access auth \
  --field sku:str:true:true --field quantity:int:true:false

forgeapi create --module-name payment --access rbac \
  --field transactionId:str:true:true --field amount:float:true:false \
  --field status:str:true:false

forgeapi create --module-name review --access public \
  --field comment:str:true:false --field rating:int:true:false

forgeapi create --module-name supplier --access auth \
  --field name:str:true:false --field contactEmail:str:false:false \
  --field phone:str:false:false

  🍃 MongoDB
  Collections are created automatically on first request inside the forgeapi database.
  forgeapi (database)
├── products
├── categories
├── customers
├── orders
├── inventories
├── payments
├── reviews
└── suppliers
Fields with unique: true automatically get a MongoDB unique index on the collection.
🌐 API Endpoints
Each module exposes standard REST endpoints:
GET    /{module}/       → list all
POST   /{module}/       → create
GET    /{module}/{id}   → get one
PUT    /{module}/{id}   → update
DELETE /{module}/{id}   → delete
Interactive docs available at http://localhost:8000/docs after starting the server.
📋 Requirements
fastapi
uvicorn
motor
pymongo
pydantic
python-dotenv
sqlalchemy
pytest
httpx
requests
Install:
pip install -r requirements.txt
📄 License
MIT



