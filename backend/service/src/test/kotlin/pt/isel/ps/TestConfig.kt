package pt.isel.ps

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.ComponentScan
import org.springframework.context.annotation.Configuration
import pt.isel.ps.mem.TransactionManagerInMem

@Configuration
@ComponentScan("pt.isel.ps")
class TestConfig {
    /*@Bean
    fun clock(): Clock = Clock.systemUTC()
*/
    @Bean
    fun trxManager() = TransactionManagerInMem()

    /*@Bean
    fun usersDomainConfig() =
        UsersDomainConfig(
            tokenSizeInBytes = 256 / 8,
            tokenTtl = Duration.ofHours(24),
            tokenRollingTtl = Duration.ofHours(1),
            maxTokensPerUser = 3,
        )*/
}
