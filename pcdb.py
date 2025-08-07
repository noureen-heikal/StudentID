import pyodbc

class PCDB:
    def __init__(self):
        # Connects to the PCDB_PROD SQL Server database
        self.connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=172.16.16.13;'
            'DATABASE=PCDB_PROD;'
            'UID=hassan;'
            'PWD=Eslsca1234;'
            'TrustServerCertificate=yes;'
        )
        
        
        self.cursor = self.connection.cursor()

    def fetch_student(self, student_credentials, db_intake):
        # Check for missing input
        if student_credentials is None:
            raise ValueError("Student credentials cannot be null.")

        # SQL query with formatting for student ID/email
        query = f"""
WITH CTE AS (
    SELECT  
        PEOPLE.PEOPLE_ID,
        (ISNULL(FIRST_NAME, N'') + ' ' + ISNULL(MIDDLE_NAME, N'')) AS Eng_FullName,
        (ISNULL(UD.ARABIC_FIRSTNAME, N'') + ' ' + ISNULL(UD.ARABIC_MIDDLENAME, N' ') + ' ' + ISNULL(UD.ARABIC_LASTNAME, N' ')) AS ARABICNAME,
        (SELECT TOP (1) Email FROM dbo.EmailAddress WHERE PeopleOrgId = PEOPLE.PEOPLE_ID AND EmailType = 'UNI') AS [Eslsca Email],
        (SELECT TOP (1) Email FROM dbo.EmailAddress WHERE PeopleOrgId = PEOPLE.PEOPLE_ID AND EmailType = 'PERS') AS [Personal Email],
        CONVERT(nvarchar(10), PEOPLE.BIRTH_DATE, 103) AS [BIRTH DATE],
        CASE WHEN DEMOGRAPHICS.GENDER = 'M' THEN 'Male' WHEN DEMOGRAPHICS.GENDER = 'F' THEN 'Female' END AS GENDER,
        CASE WHEN PEOPLE.GOVERNMENT_ID IS NULL OR PEOPLE.GOVERNMENT_ID = '' THEN '0' ELSE PEOPLE.GOVERNMENT_ID END AS GOVERNMENT_ID,
        (SELECT TOP (1) CU2.LONG_DESC 
         FROM ACADEMIC
         LEFT OUTER JOIN dbo.CODE_CURRICULUM AS CU2 ON CU2.CODE_VALUE_KEY = ACADEMIC.CURRICULUM 
         WHERE ACADEMIC.PEOPLE_ID = PEOPLE.PEOPLE_ID  
         ORDER BY ACADEMIC.REVISION_DATE DESC, ACADEMIC.REVISION_TIME DESC) AS CURRICULUM,
        (SELECT TOP (1) CODE_APPDECISION.LONG_DESC
         FROM ACADEMIC
         LEFT OUTER JOIN dbo.CODE_APPDECISION ON CODE_APPDECISION.CODE_VALUE_KEY = ACADEMIC.APP_DECISION
         WHERE ACADEMIC.PEOPLE_ID = PEOPLE.PEOPLE_ID  
         ORDER BY ACADEMIC.REVISION_DATE DESC, ACADEMIC.REVISION_TIME DESC) AS APP_DECISION,
        (SELECT TOP (1) PhoneNumber 
         FROM dbo.PersonPhone 
         WHERE PersonId = PEOPLE.PersonId) AS Phone,
        (SELECT TOP (1) CODE_APPSTATUS.LONG_DESC
         FROM ACADEMIC
         LEFT OUTER JOIN dbo.CODE_APPSTATUS ON CODE_APPSTATUS.CODE_VALUE_KEY = ACADEMIC.APP_STATUS
         WHERE ACADEMIC.PEOPLE_ID = PEOPLE.PEOPLE_ID  
         ORDER BY ACADEMIC.REVISION_DATE DESC, ACADEMIC.REVISION_TIME DESC) AS APP_STATUS,
        (SELECT TOP (1) CU1.LONG_DESC 
         FROM EDUCATION
         LEFT OUTER JOIN dbo.CODE_CURRICULUM AS CU1 ON CU1.CODE_VALUE_KEY = EDUCATION.CURRICULUM  
         WHERE EDUCATION.PEOPLE_ID = PEOPLE.PEOPLE_ID  
         ORDER BY EDUCATION.REVISION_DATE DESC, EDUCATION.REVISION_TIME DESC) AS EDUCATION,
        (SELECT TOP (1) 
            CASE WHEN CU1.ORG_NAME_1 IS NULL THEN 'No School' ELSE CU1.ORG_NAME_1 END
         FROM EDUCATION
         LEFT OUTER JOIN dbo.ORGANIZATION AS CU1 ON CU1.ORG_CODE_ID = EDUCATION.ORG_CODE_ID  
         WHERE EDUCATION.PEOPLE_ID = PEOPLE.PEOPLE_ID  
         ORDER BY EDUCATION.REVISION_DATE DESC, EDUCATION.REVISION_TIME DESC) AS School
    FROM dbo.PEOPLE
    LEFT OUTER JOIN dbo.USERDEFINEDIND AS UD ON UD.PEOPLE_ID = PEOPLE.PEOPLE_ID
    LEFT OUTER JOIN dbo.DEMOGRAPHICS ON DEMOGRAPHICS.PEOPLE_ID = PEOPLE.PEOPLE_ID
)

SELECT * FROM CTE
WHERE PEOPLE_ID LIKE '{db_intake}%' OR [Personal Email] = '{student_credentials}'
"""

        # Execute and fetch result
        self.cursor.execute(query)
        result = self.cursor.fetchall()


        return result

    def close_connection(self):
        self.connection.close()