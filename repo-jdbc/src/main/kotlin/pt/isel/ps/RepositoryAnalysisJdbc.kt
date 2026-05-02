package jdbc.pt.isel.ps

import pt.isel.ps.Analysis
import pt.isel.ps.Data
import pt.isel.ps.DataType
import pt.isel.ps.Document
import pt.isel.ps.RepositoryAnalysis
import pt.isel.ps.RepositoryDocument
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Timestamp
import java.sql.Types

class RepositoryAnalysisJdbc(
    private val con: Connection,
): RepositoryAnalysis {
    override fun createAnalysis(docId: Int, filePath: String): Analysis {
        val sql = "INSERT INTO dbo.analysis (document_id, filePath) VALUES (?, ?) RETURNING id"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, docId)
            stmt.setString(2, filePath)
            stmt.executeQuery().use { rs ->
                return if (rs.next())
                    Analysis(
                        id = rs.getInt("id"),
                        docId = docId,
                        filePath = filePath
                    )
                else {
                    throw RuntimeException("Failed to create")
                }
            }
        }
    }

    override fun getDocument(id: Int): Document? {
        val sql = """
            SELECT d.id, d.name, d.origin, d.filepath
            FROM dbo.analysis a
            JOIN dbo.document d ON d.id = a.document_id
            WHERE a.id = ?
        """.trimIndent()
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) mapRowToDocument(rs) else null
            }
        }
    }

    override fun getFilepath(analysisId: Int): String? {
        val sql = "SELECT filepath FROM dbo.analysis WHERE id =?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, analysisId)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) rs.getString("filepath") else null
            }
        }
    }

    override fun getById(id: Int): Analysis? {
        val sql = "SELECT * FROM dbo.analysis WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) mapRowToAnalysis(rs) else null
            }
        }
    }

    override fun getAll(): List<Analysis> {
        val sql = "SELECT * FROM dbo.analysis"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeQuery().use { rs ->
                val analysis = mutableListOf<Analysis>()
                while (rs.next()) analysis.add(mapRowToAnalysis(rs))
                return analysis
            }
        }
    }

    override fun save(entity: Analysis) {
        val sql =
            """
            UPDATE dbo.analysis
            SET document_id=?, filepath=?
            WHERE id=?
            """.trimIndent()
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, entity.docId)
            stmt.setString(2, entity.filePath)
            stmt.setInt(3, entity.id)
            stmt.executeUpdate()
        }
    }

    override fun deleteById(id: Int): Boolean {
        val sql = "DELETE FROM dbo.analysis WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            val rowsAffected = stmt.executeUpdate()
            return rowsAffected > 0
        }
    }

    override fun clear() {
        val sql = "TRUNCATE dbo.analysis CASCADE"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
    }

    private fun mapRowToAnalysis(rs: ResultSet): Analysis {
        return Analysis(
            id = rs.getInt("id"),
            docId = rs.getInt("document_id"),
            filePath = rs.getString("filepath")
        )
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