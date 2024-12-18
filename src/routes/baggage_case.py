from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..models.baggage_models import BaggageCase
from ..schemas.baggage_case import BaggageCaseCreate, BaggageCaseUpdate, BaggageCaseSchema, CommentCreate
from ..db import get_db
from ..security import get_current_user
from ..models.user import User
import logging
import os
import uuid
from datetime import datetime
from ..utils import construct_baggage_case_response
import pyodbc




logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ZENDESK_URL = "https://arajet.zendesk.com/api/v2/tickets"
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')  
ZENDESK_PASSWORD = os.getenv('ZENDESK_PASSWORD')  
HEADERS = {"Content-Type": "application/json"}


router = APIRouter()


@router.post("/", response_model=List[BaggageCaseSchema])
def create_baggage_cases(
    baggage_cases: List[BaggageCaseCreate],
    db: Session = Depends(get_db),  
    current_user: User = Depends(get_current_user)
):
    created_baggage_cases = []
    
    for baggage_case in baggage_cases:
        if not baggage_case.PNR:
            raise HTTPException(status_code=400, detail="PNR no puede ser nulo o vacío.")

        existing_case_query = text("""
            SELECT id FROM Minerva.bender.Tbl_Baggage_Case_Ground_Ops
            WHERE PNR = :PNR AND baggage_code = :baggage_code
        """)
        existing_case = db.execute(existing_case_query, {
            "PNR": baggage_case.PNR,
            "baggage_code": baggage_case.baggage_code
        }).fetchone()

        if existing_case:
            raise HTTPException(status_code=400, detail="El caso ya existe.")
 
        baggage_case_id = str(uuid.uuid4())
        create_case_query = text("""
            INSERT INTO Minerva.bender.Tbl_Baggage_Case_Ground_Ops (
                id, baggage_code, PNR, contact_phone, contact_email, flight_number, 
                departure_date, from_airport, to_airport, passenger_name, description, 
                issue_type, status, created_agente_name, date_create, last_updated, 
                number_ticket_zendesk, pruebas_url, direccion_envio
            ) VALUES (
                :id, :baggage_code, :PNR, :contact_phone, :contact_email, :flight_number, 
                :departure_date, :from_airport, :to_airport, :passenger_name, :description, 
                :issue_type, :status, :created_agente_name, :date_create, :last_updated, 
                :number_ticket_zendesk, :pruebas_url, :direccion_envio
            )
        """)
        db.execute(create_case_query, {
            "id": baggage_case_id,
            "baggage_code": baggage_case.baggage_code,
            "PNR": baggage_case.PNR,
            "contact_phone": baggage_case.contact_phone,
            "contact_email": baggage_case.contact_email,
            "flight_number": baggage_case.flight_number,
            "departure_date": baggage_case.departure_date,
            "from_airport": baggage_case.from_airport,
            "to_airport": baggage_case.to_airport,
            "passenger_name": baggage_case.passenger_name,
            "description": baggage_case.description,
            "issue_type": baggage_case.issue_type,
            "status": "Nuevo",
            "created_agente_name": current_user.name,
            "date_create": datetime.now(),
            "last_updated": datetime.now(),
            "number_ticket_zendesk": baggage_case.number_ticket_zendesk,
            "pruebas_url": baggage_case.pruebas_url,
            "direccion_envio": baggage_case.direccion_envio
        })

 
        if baggage_case.comments:
            for comment in baggage_case.comments:
                create_comment_query = text("""
                    INSERT INTO tbl_ground_ops_comments (baggage_case_id, text, created_at)
                    VALUES (:baggage_case_id, :text, :created_at)
                """)
                db.execute(create_comment_query, {
                    "baggage_case_id": baggage_case_id,
                    "text": comment.text,
                    "created_at": datetime.now()
                })

   
        db.commit()

        created_baggage_cases.append({
            "id": baggage_case_id,
            "baggage_code": baggage_case.baggage_code,
            "PNR": baggage_case.PNR,
            "contact_phone": baggage_case.contact_phone,
            "contact_email": baggage_case.contact_email,
            "flight_number": baggage_case.flight_number,
            "departure_date": baggage_case.departure_date,
            "from_airport": baggage_case.from_airport,
            "to_airport": baggage_case.to_airport,
            "passenger_name": baggage_case.passenger_name,
            "description": baggage_case.description,
            "issue_type": baggage_case.issue_type,
            "status": "Nuevo",
            "date_create": datetime.now(),
            "last_updated": datetime.now(),
            "number_ticket_zendesk": baggage_case.number_ticket_zendesk,
            "pruebas_url": baggage_case.pruebas_url,
            "direccion_envio": baggage_case.direccion_envio,
            "comments": [{"text": comment.text} for comment in (baggage_case.comments or [])]
        })

    return created_baggage_cases



@router.get("/", response_model=List[BaggageCaseSchema])
def get_baggage_cases(db: Session = Depends(get_db)):
    sql_query = """
    SELECT *
    FROM bender.Tbl_Baggage_Case_Ground_Ops
    """
    
    try:
        result = db.execute(text(sql_query))
        rows = result.fetchall()  
        if not rows:
            raise HTTPException(status_code=404, detail="No se encontraron registros.")  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando la consulta principal: {e}")  

    baggage_cases_dict = {}

    for row in rows:
        baggage_case_id = row[0]  
        baggage_cases_dict[baggage_case_id] = {
            'id': row[0],  
            'baggage_code': row[1],  
            'PNR': row[18],  
            'contact_phone': row[2] if row[2] else "No disponible",  
            'contact_email': row[3] if row[3] else "No disponible",  
            'flight_number': row[4], 
            'departure_date': row[5],  
            'from_airport': row[6], 
            'to_airport': row[7],  
            'passenger_name': row[8],  
            'description': row[9],  
            'issue_type': row[10],  
            'status': row[11],  
            'date_create': row[12], 
            'last_updated': row[13],  
            'direccion_envio': row[14],  
            'pruebas_url': row[15],  
            'created_agente_name': row[16],  
            'number_ticket_zendesk': row[17],  
            'comments': []  
        }

 
        sql_query_comments = """
            SELECT id, text, created_at
            FROM bender.Tbl_Ground_ops_comments
            WHERE baggage_case_id = :baggage_case_id
        """
        try:
            result_comments = db.execute(text(sql_query_comments), {'baggage_case_id': baggage_case_id})
            comments = result_comments.fetchall()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error ejecutando la consulta de comentarios: {e}")


        for comment_row in comments:
            comment = {
                'id': comment_row[0],  
                'text': comment_row[1], 
                'created_at': comment_row[2] 
            }
            baggage_cases_dict[baggage_case_id]['comments'].append(comment)

    print("Final baggage_cases_dict:", baggage_cases_dict)
   
    return list(baggage_cases_dict.values())



@router.get("/{baggage_case_id}", response_model=BaggageCaseSchema)
def get_baggage_case(
    baggage_case_id: str, db: Session = Depends(get_db)
):
    baggage_case = db.query(BaggageCase).filter(BaggageCase.id == baggage_case_id).options(joinedload(BaggageCase.comments)).first()

    if not baggage_case:
        raise HTTPException(status_code=404, detail="Baggage case not found")
    
    return construct_baggage_case_response(baggage_case)







@router.put("/{baggage_case_id}", response_model=BaggageCaseSchema)
def update_baggage_case(
    baggage_case_id: str,
    baggage_case_update: BaggageCaseUpdate,
    db: Session = Depends(get_db)
):
    try:

        result = db.execute(
            text("""SELECT * FROM bender.Tbl_Baggage_Case_Ground_Ops WHERE id = :baggage_case_id"""),
            {"baggage_case_id": baggage_case_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Baggage case not found")

        columns = [column[0] for column in result.description]
        existing_case = dict(zip(columns, result))


        update_data = baggage_case_update.dict(exclude_unset=True)
        update_data["last_updated"] = datetime.now()

        for key, value in update_data.items():
            if value is None and key in existing_case:
                update_data[key] = existing_case[key]


        db.execute(
            text(""" 
            UPDATE bender.Tbl_Baggage_Case_Ground_Ops 
            SET
                baggage_code = COALESCE(:baggage_code, baggage_code),
                PNR = COALESCE(:PNR, PNR),
                contact_phone = COALESCE(:contact_phone, contact_phone),
                contact_email = COALESCE(:contact_email, contact_email),
                passenger_name = COALESCE(:passenger_name, passenger_name),
                description = COALESCE(:description, description),
                issue_type = COALESCE(:issue_type, issue_type),
                status = COALESCE(:status, status),
                number_ticket_zendesk = COALESCE(:number_ticket_zendesk, number_ticket_zendesk),
                pruebas_url = COALESCE(:pruebas_url, pruebas_url),
                direccion_envio = COALESCE(:direccion_envio, direccion_envio),
                last_updated = :last_updated
            WHERE id = :baggage_case_id
            """),
            {"baggage_case_id": baggage_case_id, **update_data}
        )

       
        if "comments" in update_data and update_data["comments"]:
            for comment in update_data["comments"]:
                if comment.get("text"):
                   
                    try:
                        comment_id = str(comment["id"])
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Invalid comment ID format")


                    existing_comment = db.execute(
                        text(""" 
                        SELECT * FROM bender.Tbl_Ground_ops_comments 
                        WHERE baggage_case_id = :baggage_case_id 
                        AND id = :id
                        """),
                        {
                            "baggage_case_id": baggage_case_id, 
                            "id": comment_id 
                        }
                    ).fetchone()

                    if existing_comment:
                        db.execute(
                            text(""" 
                            UPDATE bender.Tbl_Ground_ops_comments 
                            SET text = :text, created_at = :created_at 
                            WHERE id = :id  
                            """),
                            {
                                "text": comment["text"],
                                "created_at": datetime.now(),
                                "id": comment_id,
                            },
                        )
                    else:
                       
                        db.execute(
                            text(""" 
                            INSERT INTO bender.Tbl_Ground_ops_comments (id, text, baggage_case_id, created_at)
                            VALUES (:id, :text, :baggage_case_id, :created_at)
                            """),
                            {   
                                "id": comment_id, 
                                "text": comment["text"],
                                "baggage_case_id": baggage_case_id,  
                                "created_at": datetime.now(),
                            },
                        )


        db.commit()

     
        updated_case = db.execute(
            text("""SELECT * FROM bender.Tbl_Baggage_Case_Ground_Ops WHERE id = :baggage_case_id"""),
            {"baggage_case_id": baggage_case_id}
        ).fetchone()

        if updated_case:
            updated_case_dict = dict(zip(columns, updated_case))
            return BaggageCaseSchema(**updated_case_dict)
        else:
            raise HTTPException(status_code=404, detail="Baggage case not found after update")

    except pyodbc.Error as e:
        db.rollback()
        print(f"SQL Error: {e}")
        raise HTTPException(status_code=500, detail="Error updating baggage case")

    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred while updating baggage case")







@router.delete("/{baggage_case_id}", response_model=dict)
def delete_baggage_case(
    baggage_case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    baggage_case = db.query(BaggageCase).filter(BaggageCase.id == baggage_case_id).first()
    
    if baggage_case is None:
        error_message = f"Baggage case with ID '{baggage_case_id}' not found."
        logger.warning(error_message)
        raise HTTPException(status_code=404, detail={"error": error_message})

    db.delete(baggage_case)
    db.commit()

    logger.info(f"Baggage case deleted: ID={baggage_case_id}, User={current_user.email}")
    return {"detail": f"Baggage case with ID '{baggage_case_id}' deleted successfully."}





@router.delete("/delete_coment/{coment_id}", response_model=dict)
def delete_coment(coment_id: str, db: Session = Depends(get_db)):
    try:

        query_select = text("SELECT id FROM bender.Tbl_Ground_ops_comments WHERE id = :coment_id")
        result = db.execute(query_select, {"coment_id": coment_id}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")

        query_delete = text("DELETE FROM bender.Tbl_Ground_ops_comments WHERE id = :coment_id")
        db.execute(query_delete, {"coment_id": coment_id})
        db.commit()

        return {"message": "Comentario eliminado exitosamente"}
    except Exception as e:
        db.rollback()  
        raise HTTPException(status_code=500, detail=f"Error eliminando el comentario: {str(e)}")
