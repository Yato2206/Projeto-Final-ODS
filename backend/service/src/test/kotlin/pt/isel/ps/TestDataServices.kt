package pt.isel.ps

import org.example.Failure
import org.example.Success
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.test.annotation.DirtiesContext
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig
import java.time.LocalDateTime
import kotlin.test.assertEquals
import kotlin.test.assertIs

@SpringJUnitConfig(TestConfig::class)
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class TestDataServices {

    @Autowired
    private lateinit var service: DataServices

    private val fixedDateChecked: LocalDateTime = LocalDateTime.of(2026, 3, 25, 0, 0)
    private val fixedDate = LocalDateTime.of(2026, 3, 25, 0, 0)

    @Test
    fun `createData creates a new Data`() {
        val data = service.createData(
            origin = "Universidade de Toronto",
            dataChecked = fixedDate
        )
        assertEquals(5, data.id)
        assertEquals(emptyList(), data.odsId)
        assertEquals("Universidade de Toronto", data.origin)
        assertEquals(DataType.UNDEFINED, data.type)
        assertEquals(fixedDate, data.dateChecked)
    }

    @Test
    fun `getAllData returns all Data`() {
        val data = service.getAlldata()
        assertEquals(5, data.size)
        assertEquals(Data(id = 0, odsId = listOf(1), type = DataType.ARTISTICO, origin = "Origin1", dateChecked = fixedDateChecked), data[0])
        assertEquals(Data(id = 1, odsId = listOf(3, 16), type = DataType.CIENTIFICO, origin = "Origin2", dateChecked = fixedDateChecked), data[1])
    }

    @Test
    fun `getDataById returns a Data`() {
        val data = service.getDataById(0)
        assertIs<Success<Data>>(data)
        assertEquals(0, data.value.id)
        assertEquals(listOf(1), data.value.odsId)
        assertEquals(DataType.ARTISTICO, data.value.type)
        assertEquals("Origin1", data.value.origin)
        assertEquals(fixedDateChecked, data.value.dateChecked)
    }

    @Test
    fun `getDataById returns error because Data inexistent`() {
        val data = service.getDataById(100)
        assertIs<Failure<DataError.NotFound>>(data)
    }

    @Test
    fun `getOds returns the ODS associated with a Data`() {
        val ods = service.getOds(1)
        assertIs<Success<List<Ods>>>(ods)
        assertEquals(2, ods.value.size)
        assertEquals(Ods(3, "Educação de Qualidade"), ods.value[0])
        assertEquals(Ods(16, "Parcerias Emprol das Metas"), ods.value[1])
    }

    @Test
    fun `getOds returns error because Data inexistent`() {
        val ods = service.getOds(100)
        assertIs<Failure<DataError.NotFound>>(ods)
    }

    @Test
    fun `getOrigin returns the correct origin`() {
        val origin = service.getOrigin(2)
        assertIs<Success<String>>(origin)
        assertEquals("Origin1", origin.value)
    }

    @Test
    fun `getOrigin fails to return an origin`() {
        val origin = service.getOrigin(100)
        assertIs<Failure<DataError.NotFound>>(origin)
    }

    @Test
    fun `getType returns the correct type`() {
        val type = service.getType(2)
        assertIs<Success<DataType>>(type)
        assertEquals(DataType.ACAO_NA_SOCIEDADE, type.value)
    }

    @Test
    fun `getType fails to return a type`() {
        val type = service.getType(100)
        assertIs<Failure<DataError.NotFound>>(type)
    }

    @Test
    fun `getDateChecked returns the correct date`() {
        val date = service.getDateChecked(2)
        assertIs<Success<LocalDateTime>>(date)
        assertEquals(fixedDateChecked, date.value)
    }

    @Test
    fun `getDateChecked fails to return a date`() {
        val date = service.getDateChecked(100)
        assertIs<Failure<DataError.NotFound>>(date)
    }

    @Test
    fun `deleteData deletes a data`() {
        val deleted = service.deleteData(2)
        assertIs<Success<Boolean>>(deleted)
        val deletedValue = deleted.value
        assertEquals(true, deletedValue)
    }

    @Test
    fun `deleteData fails to delete a data`() {
        val deleted = service.deleteData(7)
        assertIs<Failure<DataError.NotFound>>(deleted)
    }
}