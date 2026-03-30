package org.example.pt.isel.ps

/*
@ControllerAdvice
class CustomExceptionHandler : ResponseEntityExceptionHandler() {
    override fun handleMethodArgumentNotValid(
        ex: MethodArgumentNotValidException,
        headers: HttpHeaders,
        status: HttpStatusCode,
        request: WebRequest,
    ): ResponseEntity<Any>? {
        log.info("Handling MethodArgumentNotValidException: {}", ex.message)
        return Problem.InvalidRequestContent.response(HttpStatus.BAD_REQUEST)
    }

    override fun handleHttpMessageNotReadable(
        ex: HttpMessageNotReadableException,
        headers: HttpHeaders,
        status: HttpStatusCode,
        request: WebRequest,
    ): ResponseEntity<Any> {
        log.info("Handling HttpMessageNotReadableException: {}", ex.message)
        return Problem.InvalidRequestContent.response(HttpStatus.BAD_REQUEST)
    }

    @ExceptionHandler(
        Exception::class,
    )
    fun handleAll(
        req: HttpServletRequest,
        ex: Exception,
    ): ResponseEntity<Unit> {
        logger.error("Request: ${req.requestURL} raised $ex")
        return ResponseEntity.status(500).build()
    }

    companion object {
        private val log = LoggerFactory.getLogger(CustomExceptionHandler::class.java)
    }
}*/