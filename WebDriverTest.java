import java.net.URL;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.firefox.FirefoxProfile;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;

public class WebDriverTest {
    public static void main(String[] args) throws Exception {

        DesiredCapabilities capability = DesiredCapabilities.firefox();
        long before = System.currentTimeMillis();
        String IP_address = "";
        IP_address = args[0];
        System.out.println("\n\n***************************** STARTING UI TEST ****************************\n");
        boolean has_test_passed = true;

        System.out.println("Attempting to start browser session using IP address : " + IP_address +" ...  ");
        try {
            WebDriver driver = new RemoteWebDriver(new URL("http://" + IP_address + ":4444/wd/hub"), capability);
            driver.get("http://www.google.com/webhp?complete=1&hl=en");
            Actions action = new Actions(driver);
            WebElement someElement = driver.findElement(By.id("gb"));
            WebElement otherElement = driver.findElement(By.id("als"));
            action.clickAndHold(someElement).moveToElement(otherElement).release(otherElement).build().perform();
            WebElement searchElement = driver.findElement(By.name("q"));
            System.out.println("Succesfully started browser session!\nUsing browser to search for 'Bananas' ...  ");
            searchElement.sendKeys("Bananas");
            searchElement.submit();
            System.out.println("Search completed! Waiting in session ...  ");
            Thread.sleep(2000);
            driver.quit();
            System.out.println("Exited session.\nTime taken: " + (System.currentTimeMillis() - before) + "ms\n" + IP_address + ": PASSED\n");
        }
        catch(org.openqa.selenium.remote.UnreachableBrowserException e) {
            System.out.println(e + "\n\n" + IP_address + ": FAILED\n");
            has_test_passed = false;
        }
        if(has_test_passed) {
            System.out.println("\n************************** UI TEST RESULT: PASS **************************\n");
        }
        else {
            System.out.println("\n****************** UI TEST RESULT: FAIL ******************\n");
        }

    }
}
