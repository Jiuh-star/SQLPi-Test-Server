                               SQLPi Test Server
This project is developed as SQLPi test server. It implements the following
simple behavior:
    1. Echo.
    2. Compare to a fixed random value with a given comparison operator.
    3. Simple blind injection test instance.
    4. Blind injection test instance with a simple WAF.
    5. Blind injection test instance with a high latency network.
    6. Get the fixed random value.
    7. Get or reset counts of inject, compare and request.
    8. Get value in data base according to name.
And their URL and expected params are:
    1. /echo?msg=
    2. /compare/<string:comp>?val=[?target=]
    3. /inject/simple?inject=
    4. /inject/waf?inject=
    5. /inject/latency?inject=
    6. /debug/target
    7. /debug/count[?reset]
    8. /debug/db?name=
Have fun!
