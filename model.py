import psycopg2
import time

from sqlalchemy import create_engine, inspect, Column, Integer, String, Text, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Mentor(Base):
    __tablename__ = 'mentor'
    mentor_id = Column(Integer, Sequence('mentor_mentor_id_seq'), primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    projectgroups = relationship('ProjectGroup', back_populates='mentor')

class Project(Base):
    __tablename__ = 'project'
    project_id = Column(Integer, Sequence('project_project_id_seq'), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    projectgroups = relationship('ProjectGroup', back_populates='project')

class ProjectGroup(Base):
    __tablename__ = 'projectgroup'
    group_id = Column(Integer, Sequence('projectgroup_group_id_seq'), primary_key=True)
    mentor_id = Column(Integer, ForeignKey('mentor.mentor_id'))
    project_id = Column(Integer, ForeignKey('project.project_id'))
    group_name = Column(String, nullable=False)
    mentor = relationship('Mentor', back_populates='projectgroups')
    project = relationship('Project', back_populates='projectgroups')
    students = relationship('StudentProjectGroup', back_populates='projectgroup')

class Student(Base):
    __tablename__ = 'student'
    student_id = Column(Integer, Sequence('student_student_id_seq'), primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    projectgroups = relationship('StudentProjectGroup', back_populates='student')

class StudentProjectGroup(Base):
    __tablename__ = 'student_projectgroup'
    student_id = Column(Integer, ForeignKey('student.student_id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('projectgroup.group_id'), primary_key=True)
    student = relationship('Student', back_populates='projectgroups')
    projectgroup = relationship('ProjectGroup', back_populates='students')


class Model:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname='StudentProjects',
            user='postgres',
            password='1111',
            host='localhost',
            port=5432
        )
        
        self.engine = create_engine('postgresql://postgres:1111@localhost:5432/StudentProjects')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def table_names(self):
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            print(e)
            return []

    def table_columns(self, table_name):
        try:
            inspector = inspect(self.engine)
            return [column['name'] for column in inspector.get_columns(table_name)]
        except Exception as e:
            print(e)
            return []

    from sqlalchemy.orm import Session
    from sqlalchemy import create_engine

    def table_data(self, table_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
            data = cursor.fetchall()
            cursor.close()
            return data
        except Exception as e:
            print(e)
            return []

    def insert_data(self, table_name, columns, data):
        try:
            table_class = globals()[table_name.capitalize()]
            new_record = table_class(**dict(zip(columns, data)))
            self.session.add(new_record)
            self.session.commit()
            return True
        except Exception as e:
            print(e)
            self.session.rollback()
            return False

    def update_data(self, table_name, columns, data, id_name, id_value):
        try:
            table_class = globals()[table_name.capitalize()]
            record = self.session.query(table_class).filter(getattr(table_class, id_name) == id_value).first()
            if record:
                for column, value in zip(columns, data):
                    setattr(record, column, value)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(e)
            self.session.rollback()
            return False

    def delete_data(self, table_name, id_name, id_value):
        try:
            table_class = globals()[table_name.capitalize()]
            record = self.session.query(table_class).filter(getattr(table_class, id_name) == id_value).first()
            if record:
                self.session.delete(record)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(e)
            self.session.rollback()
            return False
    
    def generate_data(self, table_name, rows):
        try:
            cursor = self.conn.cursor()
            
            # get columns
            columns = self.table_columns(table_name)
            # Don't delete id column for student_projectgroup table
            if table_name != 'student_projectgroup':
                columns = columns[1:]
            
            # get data types
            data_types = []
            for column in columns:
                cursor.execute(f"SELECT data_type FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='{column}'")
                data_types.append(cursor.fetchone()[0])
                
            # find foreign keys, corresponding tables, and original key names and make a dictionary
            foreign_keys = {}
            for column in columns:
                cursor.execute(f"""
                    SELECT 
                        ccu.table_name, 
                        kcu.column_name 
                    FROM 
                        information_schema.constraint_column_usage AS ccu
                    JOIN 
                        information_schema.referential_constraints AS rc 
                        ON ccu.constraint_name = rc.constraint_name
                    JOIN 
                        information_schema.key_column_usage AS kcu 
                        ON rc.unique_constraint_name = kcu.constraint_name
                    WHERE 
                        ccu.constraint_name IN (
                            SELECT 
                                constraint_name 
                            FROM 
                                information_schema.key_column_usage 
                            WHERE 
                                table_name='{table_name}' 
                                AND column_name='{column}'
                        ) 
                        AND ccu.table_name != '{table_name}'
                """)
                foreign_key_info = cursor.fetchone()
                if foreign_key_info:
                    foreign_keys[column] = {
                        'table': foreign_key_info[0],
                        'original_key': foreign_key_info[1]
                    }

            # generate data
            for _ in range(rows):
                query = f"INSERT INTO {table_name} ("
                query += ', '.join(columns) + ') VALUES ('
                
                for column, data_type in zip(columns, data_types):
                    if data_type == 'integer':
                        if column in foreign_keys:
                            # get foreign key value
                            cursor.execute(f"SELECT {foreign_keys[column]['original_key']} FROM {foreign_keys[column]['table']} ORDER BY RANDOM() LIMIT 1")
                            query += f"(SELECT {cursor.fetchone()[0]}), "
                        else:
                            query += 'TRUNC(RANDOM() * 1000)::INTEGER, '

                    if data_type == 'character varying':
                        # Generate a 10-character string
                        data = ' || '.join(['CHR(TRUNC(RANDOM() * 26)::INTEGER + 65)' for _ in range(10)])
                        query += f"(SELECT {data}), "

                    if data_type == 'text':
                        # Generate a 20-character string
                        data = ' || '.join(['CHR(TRUNC(RANDOM() * 26)::INTEGER + 65)' for _ in range(20)])
                        query += f"(SELECT {data}), "

                    if data_type == 'date':
                        query += '''(TIMESTAMP '2023-01-01 20:00:00' +
                                    (RANDOM() * (TIMESTAMP '2023-12-31 20:00:00' -
                                                TIMESTAMP '2023-01-01 20:00:00'))), '''

                    if data_type == 'boolean':
                        query += 'RANDOM() < 0.5, '
                        
                    if data_type == 'double precision':
                        query += 'RANDOM() * 1000, '
                        
                    if data_type == 'timestamp without time zone':
                        query += '''(TIMESTAMP '2023-01-01 20:00:00' +
                                    (RANDOM() * (TIMESTAMP '2023-12-31 20:00:00' -
                                                TIMESTAMP '2023-01-01 20:00:00'))), '''
                                                
                    if data_type == 'time without time zone':
                        query += '''(TIMESTAMP '2023-01-01 20:00:00' +
                                    (RANDOM() * (TIMESTAMP '2023-12-31 20:00:00' -
                                                TIMESTAMP '2023-01-01 20:00:00'))), '''
                                                
                    if data_type == 'timestamp with time zone':
                        query += '''(TIMESTAMP '2023-01-01 20:00:00' +
                                    (RANDOM() * (TIMESTAMP '2023-12-31 20:00:00' -
                                                TIMESTAMP '2023-01-01 20:00:00'))), '''

                query = query.rstrip(', ') + ')'
                query += ' ON CONFLICT DO NOTHING '
                cursor.execute(query)

            self.conn.commit()
                        
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False
        return True
    
    def custom_query_1(self, mentor_name_pattern, min_mentor_id, max_mentor_id):
        try:
            cursor = self.conn.cursor()
            start = time.time()
            cursor.execute(f"""
                SELECT m.name AS mentor_name, pg.group_name, pg.group_id
                FROM public.mentor m
                JOIN public.projectgroup pg ON m.mentor_id = pg.mentor_id
                WHERE m.name LIKE '{mentor_name_pattern}' AND m.mentor_id BETWEEN {min_mentor_id} AND {max_mentor_id};
            """)
            t = time.time() - start
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return columns, data, t
        except Exception as e:
            print(e)
            return None
        
    def custom_query_2(self, student_name_pattern):
        try:
            cursor = self.conn.cursor()
            start = time.time()
            cursor.execute(f"""
                SELECT s.name AS student_name, p.title AS project_title
                FROM public.student s
                JOIN public.student_projectgroup spg ON s.student_id = spg.student_id
                JOIN public.projectgroup pg ON spg.group_id = pg.group_id
                JOIN public.project p ON pg.project_id = p.project_id
                WHERE p.title LIKE '%{student_name_pattern}%';
            """)
            t = time.time() - start
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return columns, data, t
        except Exception as e:
            print(e)
            return None
        
    def custom_query_3(self):
        try:
            cursor = self.conn.cursor()
            start = time.time()
            cursor.execute(f"""
                SELECT pg.group_name, m.name AS mentor_name, array_agg(s.name) AS student_names
                FROM public.projectgroup pg
                LEFT JOIN public.mentor m ON pg.mentor_id = m.mentor_id
                LEFT JOIN public.student_projectgroup spg ON pg.group_id = spg.group_id
                LEFT JOIN public.student s ON spg.student_id = s.student_id
                GROUP BY pg.group_name, m.name;
            """)
            t = time.time() - start
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return columns, data, t
        except Exception as e:
            print(e)
            return None                
    
