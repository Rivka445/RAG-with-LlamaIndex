עיצוב מערכת — תמצית טכנית

רכיבים מרכזיים
- Frontend: Angular SPA שמטפל ברישום/כניסה, גלריות שמלות, סל קניות והזמנות.
- Backend: ASP.NET Core Web API — Controllers מקבלים בקשות HTTP, Services מבצעים לוגיקה עסקית, Repositories מנהלים גישה ל-DB דרך EF Core.
- DB: SQL Server — מודלים: Users, Categories, Models/Dresses, Orders, OrderItems.

Data flow (פשוט):
Client -> HTTP API (Controllers) -> Services -> Repositories -> DbContext -> SQL Server

אבטחה ואימות
- מנגנון אימות מבוסס JWT (מוזכר בעבודת הלקוח וה-DOCs). ה-token נשמר ב-localStorage בצד הלקוח.
- יש צורך לשפר: טיפול ב-refresh tokens, הגנה על endpoints קריטיים, וחסימת גישות לפי תפקידים.

שיקולים עיצוביים
- השתמשו ב-DTOs לנתונים בין השכבות כדי למנוע חשיפת מבנה הפנימי של ה-Entities.
- טיפול באחידות שמות: ישנם כמה חוסר עקביות בין שמות (Model/Product/Dress) — כדאי לאחד.
- בדיקות: להפעיל בדיקות יחידה על Services וליצור סביבת אינטגרציה עם DB מבודד (Docker/LocalDB).
