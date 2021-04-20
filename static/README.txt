                         _____  _____  __     _____  _
                        |   __||     ||  |   |  _  ||_|
                        |__   ||  |  ||  |__ |   __|| |
                        |_____||__  _||_____||__|   |_|
                                  |__|
===============================================================================
                               sqlpi-test-server
This project is developed as sqlpi test server. It implements some simple view
and SQL injection points based on PostgreSQL:
    * Basic:
        + /basic/echo?msg=
          > Echo msg.

        + /basic/compare/<comp:string>?val=[&target=]
          > Compare the target (default a global fixed random value) to the
          > given value (val) using the specific comp (gt, ge, lt, le, eq, ne).

    * Inject:
        + Error-based:
            - /inject/error/simple?inject=
              > Simple error-based injection point.

        + Blind-based (Boolean-based and Time-based):
            - /inject/blind/waf?inject=
              > Blind injection point with a simple WAF.

            - /inject/blind/latency?inject=
              > Blind injection point with high latency.

            - /inject/blind/bad-net?inject=
              > Blind injection point with a simulating terrible bad network.

    * Debug:
        + /debug/target
          > Get the fixed random value.

        + /debug/count/<view:string>[?reset=1]
          > Get or reset the count of the view (compare/inject) requests.

        + /debug/db?name=
        + Get value in data base according to name.

Have fun!
