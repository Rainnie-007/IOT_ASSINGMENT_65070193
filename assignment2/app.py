from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, Response, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import models
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
router_v1 = APIRouter(prefix='/api/v1')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-utils

@router_v1.get('/students')
async def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@router_v1.get('/students/{student_id}')
async def get_student(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()

@router_v1.post('/students')
async def create_student(student: dict, response: Response, db: Session = Depends(get_db)):
    # TODO: Add validation
    newstudent = models.Student(firstname=student['firstname'], lastname=student['lastname'], dob=student['dob'], sex=student['sex'])
    db.add(newstudent)
    db.commit()
    db.refresh(newstudent)
    response.status_code = 201
    return newstudent

@router_v1.delete('/students/{student_id}')
async def delete_student(student_id: int, response: Response, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
        return {"delete": f" Student id {student_id} deleted successfully"}
    else:
        response.status_code = 404
        return {'message': 'Student not found'}

@router_v1.put('/students/{student_id}')
async def update_student(student_id: int, response: Response, student: dict, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if db_student:
        for key, value in student.items():
            setattr(db_student, key, value)
        db.commit()
        return {'message': f'Student with ID {student_id} updated successfully'}
    else:
        response.status_code = 404
        return {'message': f'Student ID {student_id} not found'}

    
# @router_v1.patch('/students/{student_id}')
# async def update_student(student_id: int, student: dict, db: Session = Depends(get_db)):
#     pass

# @router_v1.delete('/students/{student_id}')
# async def delete_student(student_id: int, db: Session = Depends(get_db)):
#     pass

app.include_router(router_v1)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
