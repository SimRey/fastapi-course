from .. import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# Getting all posts
@router.get("/", response_model=List[schemas.PostOut])
async def get_posts(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""):
    
    ## -----------------------------------------------------------------------------------------------------
    # Done in psycopg2
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    ## -----------------------------------------------------------------------------------------------------
    
    # Using SQLAlchemy
    posts = db.query(
        models.Post, 
        func.count(models.Vote.post_id).label("votes")).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                models.Post.id).filter(
                    models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(
    id: int, 
    db: Session = Depends(get_db),
    curent_user: int = Depends(oauth2.get_current_user)):
    
    ## -----------------------------------------------------------------------------------------------------
    # Done in psycopg2
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    ## -----------------------------------------------------------------------------------------------------

    # Using SQLAlchemy  
    post = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                models.Post.id).filter(models.Post.id == id).first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    
    return post


# Posting a new post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_posts(
    post: schemas.PostCreate, 
    db: Session = Depends(get_db),
    curent_user: int = Depends(oauth2.get_current_user)
    ):
    
    ## -----------------------------------------------------------------------------------------------------
    # Done in psycopg2
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    ## -----------------------------------------------------------------------------------------------------
    
    # Using SQLAlchemy
    new_post = models.Post(
        owner_id=curent_user.id,
        **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # To get the new post with its ID
    return new_post


# Deleting a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int, 
    db: Session = Depends(get_db),
    curent_user: int = Depends(oauth2.get_current_user)):
    
    ## -----------------------------------------------------------------------------------------------------
    # Done in psycopg2
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id),))
    # deleted_post = cursor.fetchone()
    ## -----------------------------------------------------------------------------------------------------

    # Using SQLAlchemy  
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   
    if post.owner_id != curent_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform requested action")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Updating a post
@router.put("/{id}", response_model=schemas.Post)
async def update_post(
    id: int, 
    updated_post: schemas.PostCreate, 
    db: Session = Depends(get_db),
    curent_user: int = Depends(oauth2.get_current_user)):
    
    ## -----------------------------------------------------------------------------------------------------
    # Done in psycopg2
    # cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    ## -----------------------------------------------------------------------------------------------------

    # Using SQLAlchemy
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
   
    if post.owner_id != curent_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform requested action")
    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()