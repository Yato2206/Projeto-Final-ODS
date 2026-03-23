package jdbc

import Data
import DataType
import Ods
import RepositoryData
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Timestamp
import java.time.LocalDateTime
import kotlin.use

class RepositoryDataJdbc(
    private val con: Connection,
): RepositoryData {
    override fun getOds(data: Data): List<Ods>? {
        val sql = "SELECT ods_id FROM dbo.data WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeQuery().use { rs ->
                val result = mutableListOf<Ods>()
                while (rs.next()) result.add(mapRowToOds(rs))
                return result.ifEmpty { null }
            }
        }
    }

    override fun getOrigin(dataId: Int): String {
        val sql = "SELECT origin FROM dbo.data WHERE id =?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, dataId)
            stmt.executeQuery().use { rs ->
                return rs.getString("origin")
            }
        }
    }

    override fun getType(dataId: Int): DataType {
        val sql = "SELECT type FROM dbo.data WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, dataId)
            stmt.executeQuery().use { rs ->
                return DataType.valueOf(rs.getString("type"))
            }
        }
    }

    override fun getDateChecked(dataId: Int): LocalDateTime {
        val sql = "SELECT date_checked FROM dbo.data WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, dataId)
            stmt.executeQuery().use { rs ->
                return rs.getTimestamp("date_checked").toLocalDateTime()
            }
        }
    }

    override fun getById(id: Int): Data? {
        val sql = "SELECT * FROM dbo.data WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            stmt.executeQuery().use { rs ->
                return if (rs.next()) mapRowToData(rs) else null
            }
        }
    }

    override fun getAll(): List<Data> {
        val sql = "SELECT * FROM dbo.data"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeQuery().use { rs ->
                val data = mutableListOf<Data>()
                while (rs.next()) data.add(mapRowToData(rs))
                return data
            }
        }
    }

    override fun save(entity: Data) {
        val sql =
            """
            UPDATE dbo.data
            SET ods_id=?, type=?, date_checked=?
            WHERE id=?
            """.trimIndent()
        con.prepareStatement(sql).use { stmt ->
            stmt.setObject(1, entity.odsId)
            stmt.setObject(2, entity.type)
            stmt.setTimestamp(3, Timestamp.valueOf(entity.dateChecked))
            stmt.executeUpdate()
        }
        if (!entity.odsId.isNullOrEmpty()) {
            val dataOdsSql = """
                INSERT INTO dbo.data_ods (data_id, ods_id) 
                VALUES (?, ?)
                ON CONFLICT (data_id, ods_id) DO NOTHING
            """.trimIndent()
            con.prepareStatement(dataOdsSql).use { stmt ->
                for (ods in entity.odsId) {
                    stmt.setInt(1, entity.id)
                    stmt.setInt(2, ods)
                }
            }
        }
    }

    override fun deleteById(id: Int): Boolean {
        val sql = "DELETE FROM dbo.data WHERE id=?"
        con.prepareStatement(sql).use { stmt ->
            stmt.setInt(1, id)
            val rowsAffected = stmt.executeUpdate()
            return rowsAffected > 0
        }
    }

    override fun clear() {
        val sql = "TRUNCATE dbo.data CASCADE"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
    }

    private fun mapRowToData(rs: ResultSet): Data {
        val odsId = rs.getArray("ods_id")?.let { arr ->
            (arr.array as Array<*>).map { (it as Number).toInt() } }?: emptyList()

        val type = rs.getString("type")?.let { DataType.valueOf(it) }?: DataType.UNDEFINED

        return Data(
            id = rs.getInt("id"),
            odsId = odsId,
            type = type,
            origin = rs.getString("origin"),
            dateChecked = rs.getTimestamp("date_checked").toLocalDateTime(),
        )
    }

    private fun mapRowToOds(rs: ResultSet): Ods {
        return Ods(
            id = rs.getInt("id"),
            name = rs.getString("name"),
        )
    }

}