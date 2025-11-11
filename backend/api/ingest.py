# backend/api/routes.py - Complete implementation

@router.post("/ingest", status_code=202)
async def ingest_circular(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process RBI circular PDF"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Only PDF files allowed")
        
        # 1. Save PDF temporarily
        from utils.pdf_parser import save_uploaded_pdf
        pdf_content = await file.read()
        pdf_path = await save_uploaded_pdf(pdf_content, file.filename)
        
        # 2. Parse PDF with Azure Document Intelligence
        from utils.azure_client import azure_client
        parsed = await azure_client.parse_pdf_with_document_intelligence(pdf_path)
        
        # 3. Create circular record
        circular = RBICircular(
            id=str(uuid.uuid4()),
            circular_id=f"MANUAL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=file.filename.replace('.pdf', ''),
            date_published=datetime.now(),
            url=f"manual_upload/{file.filename}",
            pdf_url=pdf_path,
            raw_text=parsed['text'],
            status="pending",
            parsed_at=datetime.now()
        )
        db.add(circular)
        await db.commit()
        
        # 4. Trigger agent cascade via Redis
        from utils.redis_client import redis_client, CHANNEL_NEW_CIRCULAR
        await redis_client.publish(CHANNEL_NEW_CIRCULAR, {
            "event_type": "new_circular_detected",
            "circular_id": circular.id,
            "title": circular.title
        })
        
        logger.info(f"✅ Ingested: {file.filename}")
        
        return {
            "message": "PDF ingestion started",
            "circular_id": circular.id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise HTTPException(500, str(e))
