package so.cohesive.samples.sba;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import so.cohesive.samples.sba.utils.Utils;

@RestController
public class HelloController {
    @Value("${appName}")
    private String appName;

    @GetMapping("/")
    public String index() {
        Integer total = Utils.sum(10, 15);
        return "Greetings from " + appName;
    }

}
