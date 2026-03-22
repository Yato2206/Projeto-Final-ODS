package jdbc

import Ods
import RepositoryOds
import java.sql.Connection
import java.sql.ResultSet

class RepositoryOdsJdbc (
    private val con: Connection,
) : RepositoryOds {

    override fun findByName(name: String): Ods? {
        val sql = "SELECT * FROM dbo.ods WHERE name = ?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setString(1, name)
            stmt.executeQuery().use {rs ->
                return if (rs.next()) mapRowToOds(rs) else null
            }
        }
    }

    override fun getById(id: Int): Ods? {
        val sql = "SELECT * FROM dbo.ods WHERE id = ?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) mapRowToOds(rs) else null
            }
        }
    }

    override fun getAll(): List<Ods> {
        val sql = "SELECT * FROM dbo.ods"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeQuery().use { rs ->
                val result = mutableListOf<Ods>()
                while (rs.next()) result.add(mapRowToOds(rs))
                return result
            }
        }
    }

    override fun save(entity: Ods) {
        TODO("Not yet implemented")
    }

    override fun deleteById(id: Int): Boolean {
        TODO("Not yet implemented")
    }

    override fun clear() {
        TODO("Not yet implemented")
    }

    private fun mapRowToOds(rs: ResultSet): Ods {
        return Ods(
            id = rs.getInt("id"),
            name = rs.getString("name"),
        )
    }
}