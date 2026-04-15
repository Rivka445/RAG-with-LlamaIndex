סקציית סכימת DB — Event Dress Rental

מפת טבלאות (מופקת מהמחלקות תחת `server/Entities`):

1) Users
- Id INT PK
- FirstName NVARCHAR
- LastName NVARCHAR
- Email NVARCHAR
- Phone NVARCHAR
- Password NVARCHAR (הערה: סיסמאות אסור לאחסן בטקסט ברור — המלצה: hash+salt)
- Role NVARCHAR
- יחסים: Orders (1..*)

2) UserPassword (DTO)
- Password NVARCHAR (המשמש להעברת סיסמאות מממשק)

3) Status
- Id INT PK
- Name NVARCHAR
- יחסים: Orders (1..*)

4) Rating
- RatingId INT PK
- Host, Method, Path, Referer, UserAgent (לניתוח בקשות)
- RecordDate DATETIME

5) Order
- Id INT PK
- OrderDate DATE (DateOnly)
- EventDate DATE (DateOnly)
- FinalPrice INT
- UserId INT FK -> Users(Id)
- Note NVARCHAR
- StatusId INT FK -> Status(Id)
- יחסים: OrderItems (1..*)

6) OrderItem
- Id INT PK
- DressId INT FK -> Dress(Id)
- OrderId INT FK -> Order(Id)

7) Model
- Id INT PK
- Name, Description, ImgUrl, BasePrice, Color, IsActive
- יחסים: Dresses (1..*), Categories (many-to-many)

8) Dress
- Id INT PK
- ModelId INT FK -> Model(Id)
- Size, Price, Note, IsActive
- יחסים: Model, OrderItems

9) Category
- Id INT PK
- Name, Description
- יחסים: Models (1..*) — many-to-many implied

הערות חשובות
- יש לוודא טיפול מתאים ב-Password (הצפנה) ושמירת מידע רגיש מחוץ לקוד המקור.
- יש לטפל ב-DateOnly של .NET (שדה תאריך) בביצועי ה-JSON וה-DB provider (הגדרות converters אם צריך).
- יש לבדוק אם קיימת טבלת join מפורשת ל-Model-Category; אם לא, יש להוסיף מפה מדויקת ב-DbContext.
