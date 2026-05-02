package pt.isel.ps

import jdbc.pt.isel.ps.DatabaseConnection
import jdbc.pt.isel.ps.TransactionManagerJdbc
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull

class RepositoryJdbcAnalysisTest {
    companion object {
        val trxManager = TransactionManagerJdbc()
        val con = DatabaseConnection.getConnection()
    }

    @BeforeTest
    fun setup() {
        val sql = "TRUNCATE dbo.analysis, dbo.document RESTART IDENTITY CASCADE;"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
        con.commit()
    }

    @Test
    fun `createAnalysis and getById returns an Analysis`(){
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val analysisCreated = repoAnalysis.createAnalysis(document.id, "filepath1")
            val analysisGot = repoAnalysis.getById(analysisCreated.id)
            val analysisExpected = Analysis(id = 1, docId = 1, filePath = "filepath1")
            assertNotNull(analysisGot)
            assertEquals(analysisExpected, analysisCreated)
            assertEquals(analysisExpected, analysisGot)
        }
    }
    
    @Test
    fun `createAnalysis and update its filepath and check changes`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val analysisCreated = repoAnalysis.createAnalysis(document.id, "filepath1")
            val analysisGot = repoAnalysis.getById(analysisCreated.id)
            assertEquals(analysisCreated, analysisGot)
            val updatedFilepath = analysisCreated.copy(filePath = "filepath3")
            assertNotEquals(updatedFilepath.filePath, analysisCreated.filePath)
            repoAnalysis.save(updatedFilepath)
            val foundUpdated = repoAnalysis.getById(updatedFilepath.id)
            assertEquals(updatedFilepath, foundUpdated)
        }
    }

    @Test
    fun `getAll returns all Analysis`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val analysisCreated = repoAnalysis.createAnalysis(document.id, "filepath1")
            val analysisCreated1 = repoAnalysis.createAnalysis(document.id, "filepath2")
            val analysisCreated2 = repoAnalysis.createAnalysis(document.id, "filepath3")
            val allAnalysis = repoAnalysis.getAll()
            assertEquals(3, allAnalysis.size)
            assertEquals(listOf(analysisCreated,analysisCreated1, analysisCreated2), allAnalysis)
        }
    }

    @Test
    fun `getDocument returns the origin of a given Document`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val analysisCreated = repoAnalysis.createAnalysis(document.id, "filepath1")
            val foundDocument = repoAnalysis.getDocument(analysisCreated.id)
            assertEquals(document, foundDocument)
        }
    }

    @Test
    fun `getFilepath returns the filepath of a given Analysis`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val analysisCreated = repoAnalysis.createAnalysis(document.id, "filepath1")
            val foundFilepath = repoAnalysis.getFilepath(analysisCreated.id)
            val expectedFilepath = "filepath1"
            assertEquals(expectedFilepath, foundFilepath)
        }
    }

    @Test
    fun `deleteById removes the Analysis`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
           val analysis = repoAnalysis.createAnalysis(document.id, "filepath1")
            val analysisDeleted = repoAnalysis.deleteById(analysis.id)
            val shouldBeNull = repoAnalysis.getById(analysis.id)
            assertEquals(true, analysisDeleted)
            assertNull(shouldBeNull)
        }
    }

    @Test
    fun `clear should clear all the repo`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val analysisCreated = repoAnalysis.createAnalysis(document.id, "filepath1")
            val analysisCreated1 = repoAnalysis.createAnalysis(document.id, "filepath2")
            val analysisCreated2 = repoAnalysis.createAnalysis(document.id, "filepath3")
            repoAnalysis.clear()
            val getShouldBeNull = repoAnalysis.getById(analysisCreated.id)
            val getShouldBeNull1 = repoAnalysis.getById(analysisCreated1.id)
            val getShouldBeNull2 = repoAnalysis.getById(analysisCreated2.id)
            val shouldBeEmpty = repoAnalysis.getAll()
            assertEquals(0, shouldBeEmpty.size)
            assertNull(getShouldBeNull)
            assertNull(getShouldBeNull1)
            assertNull(getShouldBeNull2)
        }
    }
}