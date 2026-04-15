Event Dress Rental — סקירה כללית

שם הפרויקט: Event Dress Rental
מטרה: מערכת לניהול השכרת שמלות לאירועים — ברמת ה-API וה-frontend מאפשרת יצירת קטגוריות, ניהול דגמים/שמלה, ביצוע הזמנות, וניהול משתמשים.

טכנולוגיות מרכזיות
- Frontend: Angular (Client/)
- Backend: ASP.NET Core Web API (.NET) (server/WebApiShop)
- ORM: Entity Framework Core (Entities/, Repositories/)
- DB: Microsoft SQL Server (משתמשים ב-DbContext שנוצר ע"י EF Core / Database-First)
- Logging: NLog
- Tests: xUnit + Moq

מבנה הריפו
- Client/ — פרויקט Angular (קוד מקור, שירותים, קומפוננטות)
- server/ — פתרון .NET עם פרויקטים: WebApiShop, Services, Repositories, Entities, DTOs, Tests
- README קבצים ושאר המסמכים נמצאים בתיקיות המשנה

איך להפעיל מקומית
Frontend (Client/)
- דרישות: Node.js, Angular CLI
- התקנה והרצה:
  - cd Client
  - npm install
  - ng serve
  - ברירת מחדל: http://localhost:4200

Backend (server/)
- דרישות: .NET SDK (גרסה מתאימה, סמוך ל- .NET 6/7/9 בהתאם לפרויקט), SQL Server (או Docker SQL Server)
- הרצה:
  - dotnet run --project server/WebApiShop
  - או לפתוח את `server/EventDressRental.sln` ב-Visual Studio ולהריץ
- ברירות מחדל של פורטים (מצוין ב-launchSettings): להסתכל ב-`server/WebApiShop/Properties/launchSettings.json`

הערות מיוחדות
- יש לוודא משתני סביבה/API keys אם יש מלווים חיצוניים (כגון SMTP וכו').
- הימנע מהתחברות למסדי נתונים שיתופיים בזמן הרצת בדיקות אינטגרציה.
