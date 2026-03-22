import org.junit.jupiter.api.Test
import java.time.LocalDateTime
import kotlin.test.assertEquals

class DomainTest {
    @Test
    fun `test invalid ODS (ID) `() {
        try {
            Ods(-1, "Invalid")
        } catch (e: IllegalArgumentException) {
            assertEquals("ODS ID must be greater than or equal to zero.", e.message)
        }
    }

    @Test
    fun `test invalid ODS (name)`() {
        try {
            Ods(1, "")
        } catch (e: IllegalArgumentException) {
            assertEquals("Name must not be blank", e.message)
        }
    }

    @Test
    fun `test valid ODS`() {
        var success = false
        try {
            Ods(1, "Test1")
            success = true
        } finally {
            assert(success) { "Failed to create a valid ODS instance." }
        }
    }

    @Test
    fun `test invalid Data (ID)`() {
        try {
            Data(-1, listOf(1), origin = "Origin", dateChecked = LocalDateTime.now())
        } catch (e: IllegalArgumentException) {
            assertEquals("Data ID must be greater than or equal to zero.", e.message)
        }
    }

    @Test
    fun `test invalid Data (origin)`() {
        try {
            Data(1, listOf(1), origin = "", dateChecked = LocalDateTime.now())
        } catch (e: IllegalArgumentException) {
            assertEquals("Origin must not be blank", e.message)
        }
    }

    @Test
    fun `test invalid Data (dateChecked)`() {
        try {
            Data(1, listOf(1), origin = "Origin", dateChecked = LocalDateTime.now().plusDays(1))
        } catch (e: IllegalArgumentException) {
            assertEquals("Date checked cannot be in the future.", e.message)
        }
    }

    @Test
    fun `test create a valid data with default dataType`() {
        var success = false
        try {
            val data = Data(id = 1, odsId = listOf(1), origin = "Origin", dateChecked = LocalDateTime.now())
            assertEquals(DataType.UNDEFINED, data.type)
            success = true
        } finally {
            assert(success) { "Failed to create a valid Data instance with default dataType." }
        }
    }

    @Test
    fun `test create a valid data with specified dataType`() {
        var success = false
        try {
            val data = Data(id = 2, odsId = listOf(2), type = DataType.CIENTIFICO, origin = "Origin", dateChecked = LocalDateTime.now())
            assertEquals(DataType.CIENTIFICO, data.type)
            success = true
        } finally {
            assert(success) { "Failed to create a valid Data instance with specified dataType." }
        }
    }

    @Test
    fun `test invalid Terms (ID)`() {
        try {
            Terms(-1, listOf(1), "Name", "Origin")
        } catch (e: IllegalArgumentException) {
            assertEquals("Terms ID must be greater than or equal to zero.", e.message)
        }
    }

    @Test
    fun `test invalid Terms (odsID)`() {
        try {
            Terms(1, emptyList(), "Name", "Origin")
        } catch (e: IllegalArgumentException) {
            assertEquals("ODS ID list must not be empty.", e.message)
        }
    }

    @Test
    fun `test invalid Terms (name)`() {
        try {
            Terms(1, listOf(1), "", "Origin")
        } catch (e: IllegalArgumentException) {
            assertEquals("Name must not be blank.", e.message)
        }
    }

    @Test
    fun `test invalid Terms (origin)`() {
        try {
            Terms(1, listOf(1), "Name", "")
        } catch (e: IllegalArgumentException) {
            assertEquals("Origin must not be blank.", e.message)
        }
    }

    @Test
    fun `create a valid Terms`() {
        var success = false
        try {
            Terms(1, listOf(1), "Valid Name", "Valid Origin")
            success = true
        } finally {
            assert(success) { "Failed to create a valid Terms instance." }
        }
    }
}