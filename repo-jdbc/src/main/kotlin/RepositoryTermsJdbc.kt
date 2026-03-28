package jdbc

import RepositoryTerms
import Terms
import Ods
import java.sql.Connection
import java.sql.ResultSet

class RepositoryTermsJdbc (
    private val con: Connection,
    ) : RepositoryTerms {

    override fun findByName(name: String): Terms? {
        val sql = "SELECT * FROM dbo.terms WHERE name = ?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setString(1, name)
            stmt.executeQuery().use {rs ->
                return if (rs.next()) mapRowToTerms(rs) else null
            }
        }
    }

    override fun getAllOdsTerms(odsId: Int): List<Terms> {
        val sql = "SELECT * FROM dbo.terms WHERE ods_id = ?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, odsId)
            stmt.executeQuery().use { rs ->
                val result = mutableListOf<Terms>()
                while (rs.next()) result.add(mapRowToTerms(rs))
                return result
            }
        }
    }

    override fun createTerm(odsId: Int, name: String, origin: String): Terms {
        val sql = "INSERT INTO dbo.terms (ods_id, name, origin) VALUES (?, ?, ?) RETURNING id"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, odsId)
            stmt.setString(2, name)
            stmt.setString(3, origin)
            stmt.executeQuery().use { rs ->
                return if (rs.next())
                    Terms(
                        id = rs.getInt("id"),
                        odsId = odsId,
                        name = name,
                        origin = origin
                    )
                else {
                    throw RuntimeException("Failed to insert Term")
                }
            }
        }
    }

    override fun getById(id: Int): Terms? {
        val sql = "SELECT * FROM dbo.terms WHERE id = ?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) mapRowToTerms(rs) else null
            }
        }
    }

    override fun getAll(): List<Terms> {
        val sql = "SELECT * FROM dbo.terms"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeQuery().use { rs ->
                val result = mutableListOf<Terms>()
                while (rs.next()) result.add(mapRowToTerms(rs))
                return result
            }
        }
    }

    override fun save(entity: Terms) {
        val sql =
            """
            UPDATE dbo.terms
            SET ods_id=?, name=?, origin=?
            WHERE id=?
            """.trimIndent()
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, entity.odsId)
            stmt.setString(2, entity.name)
            stmt.setString(3, entity.origin)
            stmt.setInt(4, entity.id)

            stmt.executeUpdate()
        }
    }

    override fun deleteById(id: Int): Boolean {
        val sql = "DELETE FROM dbo.terms WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            return stmt.executeUpdate() > 0
        }
    }

    override fun clear() {
        val sql = "TRUNCATE dbo.terms CASCADE"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
    }

    private fun mapRowToTerms(rs: ResultSet): Terms {
        return Terms(
            id = rs.getInt("id"),
            odsId = rs.getInt("ods_Id"),
            name = rs.getString("name"),
            origin = rs.getString("origin"),
        )
    }
}