package mem

import Ods
import RepositoryTerms
import Terms

class RepositoryTermsInMem: RepositoryTerms {
    private val terms = mutableListOf<Terms>(
        Terms(0, 0, "poverty", "Universidade de Toronto"),
        Terms(1, 0, "homeless", "Universidade de Toronto"),
        Terms(2, 0, "precarity", "Universidade de Toronto"),
        Terms(3, 1, "agriculture", "Universidade de Toronto"),
        Terms(4, 1, "nutrition", "Universidade de Toronto"),
        Terms(5, 1, "malnutrition", "Universidade de Toronto"),
        Terms(6, 2, "well being", "Universidade de Toronto"),
        Terms(7, 2, "holism", "Universidade de Toronto"),
        Terms(8, 2, "epidemics", "Universidade de Toronto")
    )

    override fun getById(id: Int): Terms? = terms.find { it.id == id }

    override fun getAll(): List<Terms> = terms.toList()

    override fun getAllOdsTerms(odsId: Int): List<Terms> = terms.filter {it.odsId == odsId}

    override fun createTerm(odsId: Int, name: String, origin: String): Terms = Terms(id = terms.size, odsId = odsId , name = name, origin = origin)

    override fun findByName(name: String): Terms? = terms.find { it.name == name }

    override fun save(entity: Terms) {
        terms.removeIf { it.id == entity.id }
        terms.add(entity)
    }

    override fun deleteById(id: Int): Boolean = terms.removeIf { it.id == id }

    override fun clear() = terms.clear()
}