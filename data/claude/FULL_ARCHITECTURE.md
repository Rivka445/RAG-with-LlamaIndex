ארכיטקטורה פרטנית — Event Dress Rental

תרשים ASCII (פירוט תהליכים)

Client (Angular SPA)
  - Components
  - Services (UserService, Api services)
  - localStorage: JWT token storage
      |
      v
WebApiShop (ASP.NET Core)
  - Middleware (logging, error handling, auth)
  - Controllers (UsersController, OrdersController, ModelsController, CategoriesController)
  - Services (business logic)
  - Repositories (data access via EF Core)
  - Entities (DbContext: EventDressRentalContext) -> SQL Server

External
  - NLog (logging, optional mail target)
  - SMTP (if configured via NLog)

Deployment model
- Monorepo; client and server can be containerized separately. The server exposes API endpoints consumed by the Angular client.

Security considerations
- Ensure TLS for production (HTTPS), secure JWT secret handling, do not store secrets in repo.
- Use hashed passwords and secure cookie/authorization policies for web clients.

Operational notes
- Add health checks to the API for liveness/readiness.
- Add migrations and seeders for reproducible local environments.
- Use CI (GitHub Actions) to run tests and build both client and server.
