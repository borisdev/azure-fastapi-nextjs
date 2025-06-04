## Deploy the FastAPI Project

You can set several variables, like:

-   `PROJECT_NAME`: The name of the project, used in the API for the docs and emails.
-   `STACK_NAME`: The name of the stack used for Docker Compose labels and project name, this should be different for `staging`, `production`, etc. You could use the same domain replacing dots with dashes, e.g. `fastapi-project-example-com` and `staging-fastapi-project-example-com`.
-   `BACKEND_CORS_ORIGINS`: A list of allowed CORS origins separated by commas.
-   `SECRET_KEY`: The secret key for the FastAPI project, used to sign tokens.
-   `FIRST_SUPERUSER`: The email of the first superuser, this superuser will be the one that can create new users.
-   `FIRST_SUPERUSER_PASSWORD`: The password of the first superuser.
-   `SMTP_HOST`: The SMTP server host to send emails, this would come from your email provider (E.g. Mailgun, Sparkpost, Sendgrid, etc).
-   `SMTP_USER`: The SMTP server user to send emails.
-   `SMTP_PASSWORD`: The SMTP server password to send emails.
-   `EMAILS_FROM_EMAIL`: The email account to send emails from.
-   `POSTGRES_SERVER`: The hostname of the PostgreSQL server. You can leave the default of `db`, provided by the same Docker Compose. You normally wouldn't need to change this unless you are using a third-party provider.
-   `POSTGRES_PORT`: The port of the PostgreSQL server. You can leave the default. You normally wouldn't need to change this unless you are using a third-party provider.
-   `POSTGRES_PASSWORD`: The Postgres password.
-   `POSTGRES_USER`: The Postgres user, you can leave the default.
-   `POSTGRES_DB`: The database name to use for this application. You can leave the default of `app`.
-   `SENTRY_DSN`: The DSN for Sentry, if you are using it.
