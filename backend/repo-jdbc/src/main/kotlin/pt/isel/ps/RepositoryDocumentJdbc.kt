package jdbc.pt.isel.ps

import pt.isel.ps.Data
import pt.isel.ps.DataType
import pt.isel.ps.Document
import pt.isel.ps.RepositoryDocument
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Timestamp
import javax.print.Doc

class RepositoryDocumentJdbc(
    private val con: Connection,
): RepositoryDocument{
    override fun createDocument(name: String, origin: String, filePath: String): Document {
        val sql = "INSERT INTO dbo.document (name, origin, filePath) VALUES (?, ?, ?) RETURNING id"
        con.prepareStatement(sql).use { stmt ->
            stmt.setString(1, name)
            stmt.setString(2, origin)
            stmt.setString(3, filePath)
            stmt.executeQuery().use { rs ->
                return if (rs.next())
                    Document(
                        id = rs.getInt("id"),
                        name = name,
                        origin = origin,
                        filePath = filePath
                    )
                else {
                    throw RuntimeException("Failed to insert document")
                }
            }
        }
    }

    override fun getDocumentsByName(name: String): List<Document> {
        val sql = "SELECT id, origin, filePath FROM dbo.document WHERE name = ? ORDER BY id"
        con.prepareStatement(sql).use { stmt ->
            stmt.setString(1, name)
            stmt.executeQuery().use { rs ->
                val result = mutableListOf<Document>()
                while (rs.next()) {
                    result.add(
                        Document(
                            id = rs.getInt("id"),
                            name = name,
                            origin = rs.getString("origin"),
                            filePath = rs.getString("filePath")
                        )
                    )
                }
                return result
            }
        }
    }

    override fun getOrigin(docId: Int): String? {
        val sql = "SELECT origin FROM dbo.document WHERE id = ?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, docId)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) rs.getString("origin") else null
            }
        }
    }

    override fun getFilepath(docId: Int): String? {
        val sql = "SELECT filePath FROM dbo.document WHERE id = ?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, docId)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) rs.getString("filePath") else null
            }
        }
    }

    override fun getById(id: Int): Document? {
        val sql = "SELECT * FROM dbo.document WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) mapRowToDocument(rs) else null
            }
        }
    }

    override fun getAll(): List<Document> {
        val sql = "SELECT * FROM dbo.document"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeQuery().use { rs ->
                val document = mutableListOf<Document>()
                while (rs.next()) document.add(mapRowToDocument(rs))
                return document
            }
        }
    }

    override fun save(entity: Document) {
        val sql =
            """
            UPDATE dbo.document
            SET name=?, origin=?, filePath=?
            WHERE id=?
            """.trimIndent()
        con.prepareStatement(sql).use { stmt ->
            stmt.setString(1, entity.name)
            stmt.setString(2, entity.origin)
            stmt.setString(3, entity.filePath)
            stmt.setInt(4, entity.id)
            stmt.executeUpdate()
        }
    }

    override fun deleteById(id: Int): Boolean {
        val sql = "DELETE FROM dbo.document WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            val rowsAffected = stmt.executeUpdate()
            return rowsAffected > 0
        }
    }

    override fun clear() {
        val sql = "TRUNCATE dbo.document CASCADE"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
    }

    private fun mapRowToDocument(rs: ResultSet): Document {
        return Document(
            id = rs.getInt("id"),
            name = rs.getString("name"),
            origin = rs.getString("origin"),
            filePath = rs.getString("filePath")
        )
    }
}