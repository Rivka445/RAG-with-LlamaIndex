דרכי התפתחות מוצעות (Roadmap)

קצר מועד (1-4 שבועות)
- תצורה של בדיקות אינטגרציה על Docker SQL Server במקום שימוש בקונקשן קבוע.
- תיקון והפעלת בדיקות קיימות תחת `server/Tests/`.
- הוספת קובץ `.env.example` או עידכון README עם כל משתני הסביבה הנדרשים.

בינוני טווח (1-3 חודשים)
- הוספת CI עם קונפיגורציית GitHub Actions: build + run tests + lint for Client.
- שיפור אבטחה: hash סיסמאות ו- JWT refresh token.
- הוספת Swagger/OpenAPI ושיפור דוקומנטציה של ה-API.

טווח ארוך (3-12 חודשים)
- Containerization ו-Helm charts / Docker Compose for full-stack local dev.
- E2E tests (Cypress/Playwright) that run Client + API flows.
- Feature: inventory management UI for admins, scheduling & calendar for events.

הערות
- עדיפות גבוהה לסביבה בדיקות אמינה לפני כל שיפור נוסף בקוד. זה יקצר את זמן הפיתוח ויקל על בדיקות regression.
