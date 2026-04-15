# Event Dress Rental — Project Overview

Project name & purpose
- Event Dress Rental (project root: [server/EventDressRental.sln](server/EventDressRental.sln)).  
  Purpose: an ASP.NET Core Web API backend + Angular frontend for managing categories, models/dresses, orders and users for a dress rental system (CRUD, authentication, ordering).

Full tech stack
- Frontend: Angular (Client/ — Angular CLI project) — see [Client/README.md](Client/README.md) and [Client/src/app/services/user-service.ts](Client/src/app/services/user-service.ts).  
- Backend: ASP.NET Core Web API (.NET 9, SDK-style projects) — host: [WebApiShop/](server/WebApiShop) (solution: [server/EventDressRental.sln](server/EventDressRental.sln)).  
- Database: Microsoft SQL Server (EF Core Database-First via EF Core Power Tools is used) — test/fixture uses a local SQL Server connection string in [DataBaseFixture.cs](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs).  
- ORM: Entity Framework Core (generated DB context / DbSets) — projects: `Entities/` and `Repositories/`.  
- Mapping: AutoMapper (referenced in repo docs: [server/.github/copilot-instructions.md](server/.github/copilot-instructions.md)).  
- Logging: NLog (mentioned in repo docs).  
- Tests: xUnit + Moq + Moq.EntityFrameworkCore (tests live under `server/Tests/`).  

Repo layout / monorepo structure
- Monorepo with separate client and server folders at repo root:
  - Client/ — Angular frontend
  - server/ — .NET solution with multiple projects (WebApiShop, Entities, Repositories, Services, DTOs, Tests)
- See solution file: [server/EventDressRental.sln](server/EventDressRental.sln)

How to install & run locally

Frontend (Client/)
- Prereqs: Node.js & Angular CLI (project README states Angular CLI v21.x).
- Install:
  - cd Client
  - npm install
- Run dev server:
  - ng serve
  - Open: http://localhost:4200/ (per [Client/README.md](Client/README.md))

Backend (server/)
- Prereqs: .NET 9 SDK, SQL Server (local or Docker), dotnet-ef if doing migrations.
- The tests and DatabaseFixture use an explicit connection string in:
  - [`Tests.DatabaseFixture`](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs)
- Run API:
  - From repo root: dotnet run --project server/WebApiShop
  - Or open the solution in Visual Studio and run (profiles exist in [server/WebApiShop/Properties/launchSettings.json](server/WebApiShop/Properties/launchSettings.json))

Ports & API base URL
- From launch settings: default API URLs:
  - HTTP: http://localhost:5216 (see [launchSettings.json](server/WebApiShop/Properties/launchSettings.json))
  - HTTPS: https://localhost:7057 (see [launchSettings.json](server/WebApiShop/Properties/launchSettings.json))
- Frontend dev server: http://localhost:4200

Environment variables / configuration
- The repo currently contains a hard-coded connection string in test fixture:
  - Data Source=DESKTOP-1VUANBN; Initial Catalog=Test;Integrated Security=True;Trust Server Certificate=True;Pooling=False  
  - See [`Tests.DatabaseFixture`](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs)
- Expected environment variables / appsettings (inferred):
  - ASPNETCORE_ENVIRONMENT (Development/Production) — used in [launchSettings.json](server/WebApiShop/Properties/launchSettings.json)
  - Connection string for EF Core / SQL Server (replace the hard-coded string in tests with an env var like `ConnectionStrings__DefaultConnection`)
  - JWT settings (issuer/secret/expiry) — auth is referenced in repo docs: [server/.github/copilot-instructions.md](server/.github/copilot-instructions.md)
- Recommendation: create `.env` or set `ASPNETCORE_ConnectionStrings__DefaultConnection` for local runs and update tests to use it.

Key workspace entry points & references
- Solution: [server/EventDressRental.sln](server/EventDressRental.sln)  
- Test fixture: [`Tests.DatabaseFixture`](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs)  
- Client auth helper: [Client/src/app/services/user-service.ts](Client/src/app/services/user-service.ts)  
- Repo engineering notes: [server/.github/repository-layer-instructions.md](server/.github/repository-layer-instructions.md) and [server/.github/copilot-instructions.md](server/.github/copilot-instructions.md)

Notes & immediate cautions
- Several integration test files under `server/Tests/TestRepository/IntegrationTest/` appear commented out and contain inconsistent type names (see TASKS for details). Review tests before running them.
- Tests currently create and delete databases using EnsureCreated/EnsureDeleted — be careful running against shared DB instances.

Database schema (actual entities)
- Users
  - Id (int)
  - FirstName (string)
  - LastName (string)
  - Email (string)
  - Phone (string)
  - Password (string)
  - Role (string)
  - Navigation: Orders (1..*)

- UserPassword (helper DTO used in services)
  - Password (string)

- Status
  - Id (int)
  - Name (string)
  - Navigation: Orders (1..*)

- Rating (audit-like entity)
  - RatingId (int), Host, Method, Path, Referer, UserAgent, RecordDate

- Order
  - Id (int)
  - OrderDate (DateOnly)
  - EventDate (DateOnly)
  - FinalPrice (int)
  - UserId (int)
  - Note (string)
  - StatusId (int)
  - Navigation: OrderItems (1..*), Status, User

- OrderItem
  - Id (int)
  - DressId (int)
  - OrderId (int)
  - Navigation: Dress, Order

- Model
  - Id (int)
  - Name (string)
  - Description (string)
  - ImgUrl (string)
  - BasePrice (int)
  - Color (string)
  - IsActive (bool)
  - Navigation: Dresses (1..*), Categories (many-to-many)

- Dress
  - Id (int)
  - ModelId (int)
  - Size (string)
  - Price (int)
  - Note (string)
  - IsActive (bool)
  - Navigation: Model, OrderItems

- Category
  - Id (int)
  - Name (string)
  - Description (string)
  - Navigation: Models (1..*)

Notes about schema
- The entities were generated by EF Core Power Tools (Database-First). They show many of the core tables and navigation properties. There is a many-to-many relationship implied between Model and Category via the `Model.Categories` collection; inspect the database or EF Core mapping for the join table name.
- Dates use `DateOnly` for order and event date; ensure your target .NET runtime supports `DateOnly` or add converters when needed.