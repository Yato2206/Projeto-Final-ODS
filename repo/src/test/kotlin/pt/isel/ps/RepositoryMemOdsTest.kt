package pt.isel.ps

import org.junit.jupiter.api.BeforeEach
import pt.isel.ps.mem.RepositoryOdsInMem
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class RepositoryMemOdsTest {
    private lateinit var repo: RepositoryOds

    @BeforeEach
        fun setUp() {
            repo = RepositoryOdsInMem()
        }

    @Test
    fun `create a ODS`() {
        val create = repo.createOds("Teste")
        assertEquals(Ods(17, "Teste"), create)
    }

    @Test
    fun `get a ODS by ID`() {
        val found = repo.getById(0)
        assertEquals(Ods(0, "Erradicação da Pobreza"), found)
    }

    @Test
    fun `get an inexistent ODS by ID`() {
        val found = repo.getById(17)
        assertNull(found)
    }

    @Test
    fun `findByName returns correct ODS`() {
        val found = repo.findByName("Erradicação da Pobreza")
        assertEquals(Ods(0, "Erradicação da Pobreza"), found)
    }

    @Test
    fun `findByName returns inexistent ODS (null)`() {
        val found = repo.findByName("Inexistent ODS")
        assertNull(found)
    }

    @Test
    fun `getAll returns all ODS`() {
        val found = repo.getAll()
        val odsList = listOf(
            Ods(0, "Erradicação da Pobreza"),
            Ods(1, "Fome Zero"),
            Ods(2, "Boa Saúde e Bem-Estar"),
            Ods(3, "Educação de Qualidade"),
            Ods(4, "Igualdade de Género"),
            Ods(5, "Água Limpa e Saneamento"),
            Ods(6, "Energia Acessível e Limpa"),
            Ods(7, "Emprego Digno e Crescimento Económico"),
            Ods(8, "Indústria, Inovação e Infraestrutura"),
            Ods(9, "Redução das Desigualdades"),
            Ods(10, "Cidades e Comunidades Sustentáveis"),
            Ods(11, "Consumo e Produção Responsáveis"),
            Ods(12, "Combate às Alterações Climáticas"),
            Ods(13, "Vida de Baixo D'Água"),
            Ods(14, "Vida Sobre a Terra"),
            Ods(15, "Paz, Justiça e Instituições Fortes"),
            Ods(16, "Parcerias Emprol das Metas")
        )
        assertEquals(odsList.size, found.size)
        assertEquals(odsList, found)
    }

    @Test
    fun `save updates an existing ODS`() {
        val updatedOds = Ods(0, "Erradicação da Pobreza Atualizada")
        repo.save(updatedOds)
        val found = repo.getById(0)
        assertEquals(updatedOds, found)
    }

    @Test
    fun `deleteById removes an existing ODS`() {
        val found = repo.getById(0)
        assertEquals(Ods(0, "Erradicação da Pobreza"), found)
        val deleted = repo.deleteById(0)
        assertEquals(true, deleted)
        val shouldBeNull = repo.getById(0)
        assertNull(shouldBeNull)
    }

    @Test
    fun `deleteById returns null`() {
        val deleted = repo.deleteById(17)
        assertEquals(false, deleted)
    }

    @Test
    fun `clear puts the ODS list empty`() {
        val cleared = repo.clear()
        assertEquals(Unit, cleared)
        val foundOds = repo.getById(0)
        assertNull(foundOds)
        val foundList = repo.getAll()
        assertEquals(emptyList<Ods>(), foundList)
        assertEquals(0, foundList.size)
    }
}