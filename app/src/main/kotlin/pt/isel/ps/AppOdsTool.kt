package org.example.pt.isel.ps

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer
import pt.isel.ps.mem.RepositoryDataInMem
import pt.isel.ps.mem.RepositoryOdsInMem
import pt.isel.ps.mem.RepositoryTermsInMem
import pt.isel.ps.mem.TransactionManagerInMem
import java.time.Clock

@Configuration
class PipelineConfigurer(
) : WebMvcConfigurer

@SpringBootApplication
class OdsToolApplication {
    //@Bean
    //fun trxManagerJdbc(): TransactionManagerJdbc = TransactionManagerJdbc()

    @Bean
    fun trxManager(): TransactionManagerInMem = TransactionManagerInMem()
    @Bean
    fun clock(): Clock = Clock.systemUTC()

    @Bean
    fun repositoryOds() = RepositoryOdsInMem()

    @Bean
    fun repositoryData() = RepositoryDataInMem()

    @Bean
    fun repositoryTerms() = RepositoryTermsInMem()

    /*@Bean
    fun usersDomainConfig() =
        UsersDomainConfig(
            tokenSizeInBytes = 256 / 8,
            tokenTtl = Duration.ofHours(24),
            tokenRollingTtl = Duration.ofHours(1),
            maxTokensPerUser = 3,
        )*/
}

fun main() {
    runApplication<OdsToolApplication>()
}


/*@Configuration
class PipelineConfigurer(
    val authenticationInterceptor: AuthenticationInterceptor,
    val authenticatedUserArgumentResolver: AuthenticatedUserArgumentResolver,
) : WebMvcConfigurer {
    override fun addInterceptors(registry: InterceptorRegistry) {
        registry.addInterceptor(authenticationInterceptor)
    }

    override fun addArgumentResolvers(resolvers: MutableList<HandlerMethodArgumentResolver>) {
        resolvers.add(authenticatedUserArgumentResolver)
    }
}

@SpringBootApplication
class PokerDiceApplication {
    @Bean
    fun passwordEncoder() = BCryptPasswordEncoder()

    @Bean
    fun tokenEncoder() = Sha256TokenEncoder()

    @Bean
    fun jdbi() =
        Jdbi
            .create(
                PGSimpleDataSource().apply {
                    setURL(Environment.getDbUrl())
                },
            ).configureWithAppRequirements()

    @Bean
    fun trxManager() = TransactionManagerInMem()

    @Bean
    fun trxManagerJdbi(jdbi: Jdbi): TransactionManagerJdbi = TransactionManagerJdbi(jdbi)

    @Bean
    fun clock(): Clock = Clock.systemUTC()

    @Bean
    fun usersDomainConfig() =
        UsersDomainConfig(
            tokenSizeInBytes = 256 / 8,
            tokenTtl = Duration.ofHours(24),
            tokenRollingTtl = Duration.ofHours(1),
            maxTokensPerUser = 3,
        )
}

fun main() {
	runApplication<PokerDiceApplication>()
}*/