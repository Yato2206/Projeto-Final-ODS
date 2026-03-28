package pt.isel.ps

import org.example.Failure
import org.example.Success
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.test.annotation.DirtiesContext
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNotEquals

@SpringJUnitConfig(TestConfig::class)
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class TestOdsServices {

    @Autowired
    private lateinit var service: OdsServices

    @Test
    fun `createOds stores ODS`() {
        println(service.getOdsById(17))
        val ods = service.createOds("Erradicação da Pobreza1")
        assertIs<Success<Ods>>(ods)
        assertEquals("Erradicação da Pobreza1", ods.value.name)
        assertEquals(17, ods.value.id)
    }

    @Test
    fun `createOds returns error because ODS already exists`() {
        service.createOds("Erradicação da Pobreza")
        val ods = service.createOds("Erradicação da Pobreza")
        assertIs<Failure<OdsError.OdsAlreadyExists>>(ods)
    }

    @Test
    fun `getAllOds returns all ODS`() {
        val odsList = service.getAllOds()
        assertEquals(17, odsList.size)
        assertEquals("Erradicação da Pobreza", odsList[0].name)
        assertEquals("Fome Zero", odsList[1].name)
    }

    @Test
    fun `getOdsById returns ODS`() {
        val ods = service.getOdsById(0)
        assertIs<Success<Ods>>(ods)
        assertEquals("Erradicação da Pobreza", ods.value.name)
        assertEquals(0, ods.value.id)
    }

    @Test
    fun `getOdsById returns error because ODS does not exist`() {
        val ods = service.getOdsById(100)
        assertIs<Failure<OdsError.NotFound>>(ods)
    }

    @Test
    fun `deleteOds deletes ODS`() {
        val odsListBefore = service.getAllOds()
        assertEquals(17, odsListBefore.size)
        val odsDeleted = service.deleteOds(0)
        assertIs<Success<Boolean>>(odsDeleted)
        val odsListAfter = service.getAllOds()
        assertNotEquals(odsListBefore.size, odsListAfter.size)
        assertEquals(16, odsListAfter.size)
    }

    @Test
    fun `deleteOds returns error because ODS does not exist`() {
        val odsDeleted = service.deleteOds(100)
        assertIs<Failure<OdsError.NotFound>>(odsDeleted)
    }
}