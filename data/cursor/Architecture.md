# Architecture Overview

High-level ASCII diagram
Client (Angular)
    |
    v
WebApiShop (ASP.NET Core Web API)
    - Controllers → Services → Repositories → EF Core (EventDressRentalContext)
    |
    v
SQL Server (EF Core Database-First)
    + External services: (optional) SMTP via NLog mail target, any 3rd-party auth providers (none found implemented)

Frontend architecture
- Client/ is an Angular SPA (see [Client/README.md](Client/README.md)).
- Routing: standard Angular router (typical for projects scaffolded with Angular CLI); entrypoint: `Client/src/main.ts`.
- State management: no dedicated store (NgRx) found in the snippets; local state + localStorage token handling (see [Client/src/app/services/user-service.ts](Client/src/app/services/user-service.ts)).
- Components / services: Services for API calls exist (example: [`UserService`](Client/src/app/services/user-service.ts) — handles login/register/update and session storage).

Backend architecture
- Solution: [server/EventDressRental.sln](server/EventDressRental.sln)
- Projects:
  - WebApiShop/ — ASP.NET Core host (controllers, middleware, Swagger, auth setup likely)
  - Services/ — business logic layer (registered in DI)
  - Repositories/ — data access layer using EF Core and `EventDressRentalContext` (Database-First)
  - Entities/ — EF Core entity classes / DbContext (generated)
  - DTOs/ — API DTOs and mapping (AutoMapper usage referenced)
  - Tests/ — unit & integration tests
- Request flow:
  - HTTP → Controller (WebApiShop.Controllers) → Service (Services/*.cs) → Repository (Repositories/*.cs) → EF Core (Entities.EventDressRentalContext) → SQL Server
- Key infra: DI (scoped repositories), AutoMapper, NLog for logging, JWT auth (per repo docs)

Database schema overview (inferred)
- Entities and DbSets (nomenclature inferred from tests/docs):
  - Users — authentication, profile
  - Categories — categories of dresses/models
  - Models / Products / Dresses — product/model entities (naming inconsistent in tests)
  - Orders — customer orders
  - OrderItems — items within an order (Order has many OrderItems; OrderItem references Product/Model)
- Relationships:
  - Category 1..* Models
  - Model/Product 1..* OrderItems
  - Order 1..* OrderItems
  - User 1..* Orders
- Concrete schema files (generated EF Core) live in `Entities/` (inspect for precise table/column names).

Authentication & auth flow
- Client stores a token in localStorage (see [Client/src/app/services/user-service.ts](Client/src/app/services/user-service.ts)). The client code generates a token in some flows for admin-created users (`generateToken()`), but production behavior should rely on server-issued JWTs. The repo docs indicate JWT is used:
  - See project notes: [server/.github/copilot-instructions.md](server/.github/copilot-instructions.md)
- Typical flow (expected):
  - Client POST /api/users/login → server validates credentials → server returns JWT (AuthUserModel) → client stores JWT in localStorage and sends Authorization header on subsequent requests.

Background jobs, queues, scheduled tasks
- None found in the provided excerpts. NLog mail target is mentioned (for alerts), but no background worker/queue code discovered.

External APIs / third-party services
- NLog (logging + mail target)
- Likely SMTP for emails (NLog mail target), possibly external identity providers if implemented later
- EF Core Power Tools (used to generate DB-first model)

Important code references
- Test fixture: [`Tests.DatabaseFixture`](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs)  
- Repository conventions and instructions: [server/.github/repository-layer-instructions.md](server/.github/repository-layer-instructions.md)  
- Project-level copilot notes: [server/.github/copilot-instructions.md](server/.github/copilot-instructions.md)

Detailed DB schema (fields from `server/Entities`)

- Users
  - Id: int
  - FirstName: string
  - LastName: string
  - Email: string
  - Phone: string
  - Password: string
  - Role: string
  - Orders: ICollection<Order>

- Status
  - Id: int
  - Name: string
  - Orders: ICollection<Order>

- Order
  - Id: int
  - OrderDate: DateOnly
  - EventDate: DateOnly
  - FinalPrice: int
  - UserId: int
  - Note: string
  - StatusId: int
  - OrderItems: ICollection<OrderItem>
  - Status: Status
  - User: User

- OrderItem
  - Id: int
  - DressId: int
  - OrderId: int
  - Dress: Dress
  - Order: Order

- Model
  - Id: int
  - Name: string
  - Description: string
  - ImgUrl: string
  - BasePrice: int
  - Color: string
  - IsActive: bool
  - Dresses: ICollection<Dress>
  - Categories: ICollection<Category>

- Dress
  - Id: int
  - ModelId: int
  - Size: string
  - Price: int
  - Note: string
  - IsActive: bool
  - Model: Model
  - OrderItems: ICollection<OrderItem>

- Category
  - Id: int
  - Name: string
  - Description: string
  - Models: ICollection<Model>

Auth flow (observed)
- Client holds JWT in localStorage (see `Client/src/app/services/user-service.ts`).
- Server is expected to issue tokens on login and validate them for protected endpoints. Consider adding refresh tokens and role-based checks for admin functionality.

Integration tests & DB notes
- `server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs` currently includes a hard-coded SQL Server connection string and uses EnsureCreated/EnsureDeleted. Replace with env/config-driven connection string or use ephemeral Docker DB for CI.

External services
- NLog (logging) with `nlog.config` present in `WebApiShop/`.
- No external OAuth providers or payment gateways were found in the codebase.