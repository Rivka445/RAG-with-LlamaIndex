# Tasks & TODOs (living board)

Summary of explicit TODO/FIXME/HACK tokens
- Scanned workspace excerpts: no explicit `// TODO`, `// FIXME`, `// HACK` tokens found in the provided excerpts.

Code issues, inconsistencies and actionable TODOs (inferred)
- [ ] server/Tests/TestRepository/IntegrationTest/OrderRepositoryIntegrationTests.cs:0 — file is commented out and not active. Review and restore/convert to current context types ([server/Tests/TestRepository/IntegrationTest/OrderRepositoryIntegrationTests.cs](server/Tests/TestRepository/IntegrationTest/OrderRepositoryIntegrationTests.cs))
- [ ] server/Tests/TestRepository/IntegrationTest/UserRepositoryIntegrationTests.cs:0 — file is commented out and references `WebApiShopContext` while fixture creates `EventDressRentalContext` (mismatch). Fix types and uncomment ([server/Tests/TestRepository/IntegrationTest/UserRepositoryIntegrationTests.cs](server/Tests/TestRepository/IntegrationTest/UserRepositoryIntegrationTests.cs))
- [ ] server/Tests/TestRepository/IntegrationTest/CategoryRepositoryIntegratienTests.cs:0 — file commented out and contains typos in class name. Reconcile and re-enable ([server/Tests/TestRepository/IntegrationTest/CategoryRepositoryIntegratienTests.cs](server/Tests/TestRepository/IntegrationTest/CategoryRepositoryIntegratienTests.cs))
- [ ] server/Tests/TestRepository/IntegrationTest/ProductRepositoryIntegrationTests.cs:0 — references `ModelRepository` vs `ProductRepository` mismatch. Fix naming and implementation ([server/Tests/TestRepository/IntegrationTest/ProductRepositoryIntegrationTests.cs](server/Tests/TestRepository/IntegrationTest/ProductRepositoryIntegrationTests.cs))
- [ ] server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs:0 — contains hard-coded SQL Server connection string. Replace with environment-based config and avoid committing secrets ([server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs))
- [ ] Client/src/app/services/user-service.ts:28 — `generateToken()` used for admin-created users: replace with server-issued token flow and remove client-side token generation in production ([Client/src/app/services/user-service.ts](Client/src/app/services/user-service.ts))

Missing tests / coverage gaps
- Many integration tests are commented out. Unit tests for repositories and services appear incomplete in `server/Tests/`. Add:
  - Unit tests for Services (business logic)
  - Integration tests that use a test DB with migrations or Testcontainers (avoid EnsureDeleted/EnsureCreated on shared DB)
  - API controller tests (WebApiShop controllers)

Suggested immediate next steps
- Replace hard-coded DB connection in [`Tests.DatabaseFixture`](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs) with configuration via environment variables.
- Unify context/class names across tests and projects (EventDressRentalContext vs WebApiShopContext).
- Re-enable and fix integration tests; prefer ephemeral DB instances (Docker SQL Server / LocalDB) or use in-memory provider for unit tests.
- Add CI configuration (GitHub Actions) to run unit tests and build both Client and server.
- Add a README for server showing how to seed DB and run migrations.

Roadmap — what to build next
- Authentication hardening: implement proper JWT issuance, refresh tokens, and secure storage.
- Add e2e tests linking Client ↔ API (Cypress / Playwright).
- Add CI/CD pipeline with Docker-based staging environment.
- Implement role-based access control and admin UI for managing inventory.
- Add API versioning and OpenAPI/Swagger improvements.

Searchable list of the key files referenced
- [server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs](server/Tests/TestRepository/IntegrationTest/DataBaseFixture.cs) (`Tests.DatabaseFixture`)  
- [server/Tests/TestRepository/IntegrationTest/OrderRepositoryIntegrationTests.cs](server/Tests/TestRepository/IntegrationTest/OrderRepositoryIntegrationTests.cs)  
- [server/Tests/TestRepository/IntegrationTest/UserRepositoryIntegrationTests.cs](server/Tests/TestRepository/IntegrationTest/UserRepositoryIntegrationTests.cs)  
- [server/Tests/TestRepository/IntegrationTest/CategoryRepositoryIntegratienTests.cs](server/Tests/TestRepository/IntegrationTest/CategoryRepositoryIntegratienTests.cs)  
- [server/Tests/TestRepository/IntegrationTest/ProductRepositoryIntegrationTests.cs](server/Tests/TestRepository/IntegrationTest/ProductRepositoryIntegrationTests.cs)  
- [Client/src/app/services/user-service.ts](Client/src/app/services/user-service.ts)

Additional inferred TODOs (schema & code hygiene)
- [ ] server/Entities/Model.cs — verify many-to-many mapping with Category: ensure join table exists and mapping is explicit in DbContext if code-first migrations are used.
- [ ] server/Entities/Order.cs — `OrderDate` and `EventDate` are `DateOnly` types: ensure JSON serialization settings and DB provider mapping handle DateOnly correctly.
- [ ] server/Entities/Rating.cs — audit-like entity exists but is not referenced elsewhere; confirm usage or remove if obsolete.
- [ ] server/Repositories/ & server/Services/ — add unit tests for each public method; ensure exception handling and null checks are covered.

Developer checklist before CI
- Replace hard-coded DB connection strings in tests with env-based configuration.
- Add a GitHub Actions workflow to run `dotnet test` for server and `npm ci && npm run test` (if available) for Client.
- Add a seed script or migration instruction to `server/README.md` for local developer setup.

Where to start
- Fix `DataBaseFixture` to use a local Docker SQL Server (recommended) and run integration tests against ephemeral DBs. This is the highest priority to get green CI.