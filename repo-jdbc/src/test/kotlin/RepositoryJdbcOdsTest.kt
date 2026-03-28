import jdbc.DatabaseConnection
import jdbc.TransactionManagerJdbc
import org.junit.jupiter.api.Test
import java.time.Instant
import java.time.temporal.ChronoUnit.SECONDS
import kotlin.run
import kotlin.test.BeforeTest
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull

class RepositoryJdbcOdsTest {
    companion object {
        val trxManager = TransactionManagerJdbc()
        val con = DatabaseConnection.getConnection()
    }

    @BeforeTest
    fun setup() {
        val sql = "TRUNCATE dbo.ods RESTART IDENTITY CASCADE;"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
        con.commit()
    }

    @Test
    fun `createOds and getById returns an ODS`() {
        trxManager.run {
            val odsCreated = repoOds.createOds("Erradicação da Pobreza")
            val odsGot = repoOds.getById(odsCreated.id)
            val odsExpected = Ods(1, "Erradicação da Pobreza")
            assertNotNull(odsGot)
            assertEquals(odsExpected, odsCreated)
            assertEquals(odsExpected, odsGot)
        }
    }

    @Test
    fun `findByName returns an ODS`() {
        trxManager.run {
            val odsCreated = repoOds.createOds("Erradicação da Pobreza")
            val odsGot = repoOds.findByName("Erradicação da Pobreza")
            assertNotNull(odsGot)
            assertEquals(odsCreated, odsGot)
        }
    }


    @Test
    fun `createOds and update its name and check changes`() {
        trxManager.run {
            val odsCreated = repoOds.createOds("Erradicação da Pobreza")
            val odsGot = repoOds.getById(odsCreated.id)
            assertEquals(odsCreated, odsGot)
            val updatedOds = odsCreated.copy(name = "ODS test")
            repoOds.save(updatedOds)
            val foundUpdated = repoOds.getById(odsCreated.id)
            assertEquals(updatedOds, foundUpdated)
        }
    }

    @Test
    fun `getAll returns all ODS`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val ods1 = repoOds.createOds("Fome Zero")
            val ods2 = repoOds.createOds("Boa Saúde e Bem-Estar")
            val allOds = repoOds.getAll()
            assertEquals(3, allOds.size)
            assertEquals(listOf(ods, ods1, ods2), allOds)
        }
    }

    @Test
    fun `deleteById removes the ODS`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val odsDeleted = repoOds.deleteById(ods.id)
            val shouldBeNull = repoOds.getById(ods.id)
            assertEquals(true, odsDeleted)
            assertNull(shouldBeNull)
        }
    }

    @Test
    fun `clear should clear all the repo`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val ods1 = repoOds.createOds("Fome Zero")
            val ods2 = repoOds.createOds("Boa Saúde e Bem-Estar")
            repoOds.clear()
            val getShouldBeNull = repoOds.getById(ods.id)
            val getShouldBeNull1 = repoOds.getById(ods1.id)
            val getShouldBeNull2 = repoOds.getById(ods2.id)
            val shouldBeEmpty = repoOds.getAll()
            assertEquals(0, shouldBeEmpty.size)
            assertNull(getShouldBeNull)
            assertNull(getShouldBeNull1)
            assertNull(getShouldBeNull2)
        }
    }
}