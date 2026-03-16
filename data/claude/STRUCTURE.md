מבנה הקבצים ועץ פרויקט (קצר)

תיקיות עיקריות:
- Client/ — פרויקט Angular
  - src/app/ — רכיבי ה-frontend, שירותים ונתיבים
  - angular.json, package.json

- server/ — פתרון .NET
  - WebApiShop/ — host עם Controllers ו-Program.cs
  - Services/ — לוגיקה עסקית
  - Repositories/ — גישת נתונים + EF usage
  - Entities/ — מחלקות ה-Entity וה-DbContext
  - DTOs/ — Data Transfer Objects
  - Tests/ — בדיקות יחידה ואינטגרציה

קבצי כניסה חשובים:
- server/EventDressRental.sln — קובץ ה-solution
- server/WebApiShop/Properties/launchSettings.json — הגדרות פורט ותצורת הרצה
- Client/src/main.ts — entry point ל-Angular

המלצות ניווט מהיר
- להתחיל בבדיקה של `server/WebApiShop/` כדי לראות Controllers ו-Endpoints.
- לעיין ב-`Entities/` כדי להבין את סכימת ה-DB המדויקת.
- להפעיל `Client/` עם `ng serve` ולראות את ה-UI שמתקשר ל-API.
