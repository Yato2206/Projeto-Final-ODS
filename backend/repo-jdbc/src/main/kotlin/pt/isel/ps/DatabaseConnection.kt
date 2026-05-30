package jdbc.pt.isel.ps

import org.postgresql.ds.PGSimpleDataSource
import java.sql.Connection

/**
 * Objeto realizado para gerir as ligações à base de dados.
 * Este objeto fornece um método para obter uma ligação à base de dados `PostgreSQL`
 * utilizando o URL JDBC especificado na variável de ambiente DB_URL.
 * A ligação está configurada para não efetuar auto-commit das transações, permitindo
 * a gestão manual das transações.
 */
object DatabaseConnection {
    private val dataSource =
        PGSimpleDataSource().apply {
            setURL(Environment.getDbUrl())
        }

    fun getConnection(): Connection {
        val con = dataSource.connection
        con.autoCommit = false
        return con
    }
}