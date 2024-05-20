import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import datetime
import tools
import time

def port(mongo_db, files):
    collection_name = 'course'
    cou = mongo_db[collection_name]
    cou.delete_many({})
    cou.create_index("id", unique=True)
    sem = mongo_db["semester"]
    loc = mongo_db["location"]
    for file in files:
        logging.info("enter "+ file)
        semester_shortname = str.split(file, ".")[0].lower()
        sem_id = sem.find_one({"id1": semester_shortname})['id1']
        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
        # cur = conn.cursor()
        table_name = "Course"
        trans = {'id': 'shortname', 'href': 'url', 'notes': 'comment_latex'}
        skip = ['lsfid']
        logging.info("Entering " + table_name)
        df = pd.read_sql_query(f"SELECT * from {table_name}", conn)
        df.rename(columns = trans, inplace = True)
        df.drop(skip, axis='columns', inplace = True)
        df['semester'] = [sem_id for x in df['shortname']]
        df['ects'] = [str(x) for x in df['ects']]
        df['id'] = [semester_shortname + "-" + x.lower() for x in df['shortname']]
        posts = df.to_dict('records')
        for x in posts:
            rem = []
            for key, value in x.items():
                if x[key] is None:
                    rem.append(key)
            for a in rem:
                del x[a]
                logging.debug("Deleted " + a)
        for x in posts:
            cou.insert_one(x)
        logging.info("Updated course in semester " + semester_shortname)

        # Update from CourseCategory
        cat = mongo_db['course_category']
        df = pd.read_sql_query("SELECT * from CourseCategory", conn)
        df['category_id'] = df['category_id'].astype('Int32')
        for index, row in df.iterrows():
            my_course = cou.find_one({"shortname": row['course_id'], 'semester': sem_id})['id']
            my_cat = cat.find_one({"rank": row['category_id'], 'semester': sem_id})['id']
            cat.update_one({"rank": row['category_id'], 'semester': sem_id},  {'$push': {'courses': my_course}})
            cou.update_one({"shortname": row['course_id'], 'semester': sem_id},  {'$set': {'category': my_cat}})
        logging.info("updated course_category in semester " + semester_shortname)

        # Update from CourseCode
        code = mongo_db['code']
        df = pd.read_sql_query("SELECT * from CourseCode", conn)
        for index, row in df.iterrows():
            my_course = cou.find_one({"shortname": row['course_id'], 'semester': sem_id})['id']
            my_code = code.find_one({"rank": row['code_id'], 'semester': sem_id})['id']
            code.update_one({"rank": row['code_id'], 'semester': sem_id},  {'$push': {'courses': my_course}})
            cou.update_one({"shortname": row['course_id'], 'semester': sem_id},  {'$push': {'code': my_code}})
        logging.info("updated course_code in semester " + semester_shortname)

        # Update from Exam
        df = pd.read_sql_query("SELECT * from Exam", conn)
        df = df.fillna(0)
        def datetime_begin(row):
            return datetime.datetime(year = int(row['year']), month = int(row['month']), day = int(row['day']), hour = int(row['h']), minute = int(row['m']))
        def datetime_end(row):
            return datetime.datetime(year = int(row['year']), month = int(row['month']), day = int(row['day']), hour = int(row['hend']), minute = int(row['mend']))        
        df['begin_date'] = df.apply(datetime_begin, axis=1)
        df['end_date'] = df.apply(datetime_end, axis=1)
        df["key"] = ['Klausur' if x == 0 else "Wiederholungsklausur" for x in df['retry_exam']]
        df_room = pd.read_sql_query("SELECT * from ExamRoom", conn)
        for index, row in df.iterrows():
            room_list_shortname = list(df_room[df_room['exam_id'] == row['id']]['place_id'])
            my_places = [x['id'] for x in loc.find({'shortname': {'$in': room_list_shortname}})]
            newdate =   { 'calendar_dates': 
                            {
                                'key': row['key'], 'date_begin': row['begin_date'], 'date_end': row['end_date'] 
                            },
                            'locations': my_places
                        } 
            cou.update_one({"shortname": row['course_id'], 'semester': sem_id}, {'$push': newdate} )
        logging.info("updated Exam in semester " + semester_shortname)

        # Update from Lecture
        df_lecture = pd.read_sql_query("SELECT * from Lecture", conn)
        df_lecture = df_lecture.fillna("")
        df_lecture_booking = pd.read_sql_query("SELECT * from LectureRecurrentBooking", conn)
        df_lecture_booking = df_lecture_booking.fillna(0)
        
        def datetime_begin(row):
            return datetime.datetime(year = 1970, month = 1, day = 1, hour = int(row['h']), minute = int(row['m']))
        def datetime_end(row):
            return datetime.datetime(year = 1970, month = 1, day = 1, hour = int(row['hend']), minute = int(row['mend']))
        df_lecture_booking['start_time'] = df_lecture_booking.apply(datetime_begin, axis=1)
        df_lecture_booking['end_time'] = df_lecture_booking.apply(datetime_end, axis=1)
        wd = {"1": "Montag", "2": "Dienstag", "3": "Mittwoch", "4": "Donnerstag", "5": "Freitag", "6": "Samstag", "7": "Sonntag"}
        df_lecture_booking['weekday'] = [wd[str(x)] for x in df_lecture_booking['weekday']]
        for index, row in df_lecture_booking.iterrows():
            if not row['place_id'] == 0:
                my_place = loc.find_one({'shortname': row['place_id']})['id']
            my_course_shortname = list(df_lecture[df_lecture['id'] == row['lecture_id']]['course_id'])[0]
            my_course_typ       = list(df_lecture[df_lecture['id'] == row['lecture_id']]['typ'])[0]
            newdate =   { 'weekly_dates': 
                            {
                                'key': my_course_typ, 'weekday': row['weekday'], 'start_time': row['start_time'], 'end_time': row['end_time'] 
                            }
                        } 
            if not row['place_id'] == 0:
                newdate['weekly_dates']['location'] = my_place
            cou.update_one({"shortname": my_course_shortname, 'semester': sem_id}, {'$push': newdate} )
        logging.info("updated Lecture in semester " + semester_shortname)
        
        # Update from Exercises
        df_exercises = pd.read_sql_query("SELECT * from Exercises", conn)
        df_exercises = df_exercises.fillna("")
        for item, row in df_exercises.iterrows():
            cou.update_one({'shortname': row['course_id'], "semester": sem_id}, {'$push': {'weekly_dates': {'key': row['typ']}}})
        logging.info("updated Exercises in semester " + semester_shortname)

        # Update from Lecturer
        df_lecturer = pd.read_sql_query("SELECT * from Lecturer", conn)
        df_lecturer = df_lecturer.fillna("")
        df_person = pd.read_sql_query("SELECT * from Person", conn)
        per = mongo_db['person']
        for item, row in df_lecturer.iterrows():
            my_person_name = list(df_person[df_person['id'] == row['person_id']]['name'])[0]
            my_person = per.find_one({'name': my_person_name})['id']
            cou.update_one({'shortname': row['course_id'], "semester": sem_id}, {'$push': {'dozenten': my_person}})
        logging.info("updated Lecturer in semester " + semester_shortname)

        # Update from Tutor and Tutorial
        df_tutor = pd.read_sql_query("SELECT * from Tutor", conn)
        df_tutor = df_tutor.fillna("")
        df_tutorial = pd.read_sql_query("SELECT * from Tutorial", conn)
        df_tutorial = df_tutorial.fillna("")
        df_person = pd.read_sql_query("SELECT * from Person", conn)
        per = mongo_db['person']
        for item, row in df_tutor.iterrows():
            my_course_id = list(df_tutorial[df_tutorial['id'] == row['tutorial_id']]['course_id'])[0]
            my_person_name = list(df_person[df_person['id'] == row['person_id']]['name'])[0]
            my_person = per.find_one({'name': my_person_name})['id']
            cou.update_one({'shortname': my_course_id, "semester": sem_id}, {'$push': {'assistenten': my_person}})
        for item, row in df_tutorial.iterrows():
            cou.update_one({'shortname': row['course_id'], "semester": sem_id}, {'$push': {'weekly_dates': {'key': row['typ']}}})
        logging.info("updated Tutor and Tutorial in semester " + semester_shortname)

        # Update from Requirement and CourseRequirement
        df_cou_req = pd.read_sql_query("SELECT * from CourseRequirement INNER JOIN Requirement ON Requirement.id = CourseRequirement.requirement_id", conn)
        df_cou_req = df_cou_req.fillna("")
        pro = mongo_db['program']
        mod = mongo_db['module']
        for item, row in df_cou_req.iterrows():
            my_program = pro.find_one({'id': row['program_id']})['id'] 
            my_module = mod.find_one({'id': row['module_id']})['id'] 
            my_course = cou.find_one({'shortname': row['course_id'], "semester": sem_id})['id']
            if row['type'] == "study":
                if cou.find_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} } ):
                    cou.update_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} }, {'$push': {'usabilities.$.sl': row['desc']}})
                else:
                    cou.update_one({'id': my_course}, {'$push': {'usabilities': { 'program': my_program, 'module': my_module} } } )
                    cou.update_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} }, {'$push': {'usabilities.$.sl': row['desc']}})
            elif row['type'] == "exam":
                if cou.find_one({'_id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} } ):
                    cou.update_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} }, {'$push': {'usabilities.$.pl': row['desc']}})
                else:
                    cou.update_one({'id': my_course}, {'$push': {'usabilities': { 'program': my_program, 'module': my_module} } } )
                    cou.update_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} }, {'$push': {'usabilities.$.pl': row['desc']}})
            elif row['type'] == "comment":
                if cou.find_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} } ):
                    cou.update_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} }, {'$push': {'usabilities.$.comment': row['desc']}})
                else:
                    cou.update_one({'id': my_course}, {'$push': {'usabilities': { 'program': my_program, 'module': my_module} } } )
                    cou.update_one({'id': my_course, 'usabilities': { '$elemMatch': {'program': my_program, 'module': my_module }} }, {'$push': {'usabilities.$.comment': row['desc']}})
        logging.info("updated Requirements in semester " + semester_shortname)

    import schema
    mongo_db.command("collMod", "course", validator = schema.course_validator)
