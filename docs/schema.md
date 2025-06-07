## 資料表

### UserInfo

| 欄位名稱        | 資料型別     | 限制             | 說明                                   |
| --------------- | ------------ | ---------------- | -------------------------------------- |
| `uniq_id`       | varchar(60)  | PK, NOT NULL     | 使用者唯一識別碼（不可重複，作為主鍵） |
| `name`          | nvarchar(50) | NOT NULL         | 使用者姓名                             |
| `email`         | nvarchar(50) | UNIQUE, NOT NULL | 使用者電子郵件，需唯一                 |
| `password_hash` | varchar(60)  | NOT NULL         | 密碼的加密雜湊值（例如使用 bcrypt）    |
| `access_token`  | varchar(60)  | NOT NULL         | 使用者登入後的權杖，用於身份驗證       |
| `login_time`    | datetime     | 可為 NULL        | 使用者最近一次登入時間                 |

```
CREATE TABLE UserInfo (
    uniq_id varchar(60) NOT NULL PRIMARY KEY,
    name nvarchar(50) NOT NULL,
    email nvarchar(50) NOT NULL UNIQUE,
    password_hash varchar(60) NOT NULL,
    access_token varchar(60) NOT NULL,
    login_time datetime
);
```

### Form

| 欄位名稱      | 資料型別     | 限制                  | 說明                             |
| ------------- | ------------ | --------------------- | -------------------------------- |
| `form_id`     | varchar(60)  | PK, NOT NULL          | 表單唯一識別碼                   |
| `created_by`  | varchar(60)  | FK → UserInfo.uniq_id | 建立者的使用者 ID                |
| `created_at`  | datetime     | 預設為 GETDATE()      | 建立時間                         |
| `expire_at`   | datetime     | 可為 NULL             | 表單過期時間（可選）             |
| `invite_code` | nvarchar(10) | UNIQUE, NOT NULL      | 填表邀請碼，供填寫者進入表單使用 |

```
CREATE TABLE Form (
    form_id varchar(60) NOT NULL PRIMARY KEY,
    created_by varchar(60) NOT NULL,
    created_at datetime DEFAULT GETDATE(),
    expire_at datetime,
    invite_code nvarchar(10) NOT NULL UNIQUE,
    FOREIGN KEY (created_by) REFERENCES UserInfo(uniq_id)
);
```

### Person

| 欄位名稱     | 資料型別     | 限制                            | 說明                             |
| ------------ | ------------ | ------------------------------- | -------------------------------- |
| `person_uid` | varchar(60)  | PK, NOT NULL                    | 被回饋者唯一識別碼 ID            |
| `email`      | nvarchar(50) | NOT NULL                        | 被回饋者 email（每份表單內唯一） |
| `name`       | nvarchar(50) | NOT NULL                        | 被回饋姓名                       |
| `created_by` | nvarchar(50) | FK → UserInfo.uniq_id, NOT NULL | 用於哪個使用者                   |

```
CREATE TABLE Person(
	person_uid  varchar(60)  NOT NULL PRIMARY KEY,
    email nvarchar(50) NOT NULL,
    name nvarchar(50) NOT NULL,
    created_by varchar(60)  NOT NULL,
    FOREIGN KEY (created_by) REFERENCES UserInfo(uniq_id)
);
```

### Respondent

| 欄位名稱     | 資料型別    | 限制                          | 說明               |
| ------------ | ----------- | ----------------------------- | ------------------ |
| `form_id`    | varchar(60) | PK (與 person_uid), FK → Form | 對應的表單 ID      |
| `person_uid` | varchar(60) | PK (與 form_id), FK → Person  | 被回饋者唯一識別碼 |

```
CREATE TABLE Respondent (
    form_id    varchar(60) NOT NULL,
    person_uid varchar(60) NOT NULL,
    PRIMARY KEY (form_id, person_uid),
    FOREIGN KEY (form_id)    REFERENCES Form(form_id),
    FOREIGN KEY (person_uid) REFERENCES Person(person_uid)
);
```

### Feedback

| 欄位名稱           | 資料型別       | 限制                                | 說明               |
| ------------------ | -------------- | ----------------------------------- | ------------------ |
| `form_id`          | varchar(60)    | PK (與 person_uid), FK → Respondent | 對應的表單 ID      |
| `person_uid`       | varchar(60)    | PK (與 form_id), FK → Respondent    | 被回饋者唯一識別碼 |
| `feedback_content` | nvarchar(1000) | NOT NULL                            | 被回饋內容         |

```
CREATE TABLE Feedback (
    form_id varchar(60) NOT NULL,
    person_uid varchar(60) NOT NULL,
    feedback_content nvarchar(1000) NOT NULL,
    PRIMARY KEY (form_id, person_uid),
    FOREIGN KEY (form_id, person_uid) REFERENCES Respondent(form_id, person_uid)
);
```
