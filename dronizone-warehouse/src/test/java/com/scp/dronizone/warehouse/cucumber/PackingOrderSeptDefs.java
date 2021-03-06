package com.scp.dronizone.warehouse.cucumber;

import com.scp.dronizone.warehouse.entity.Order;
import cucumber.api.java.en.Given;
import cucumber.api.java.en.Then;
import cucumber.api.java.en.When;
import org.junit.After;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.data.mongo.DataMongoTest;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.web.client.RestTemplate;

import java.util.List;

import static org.junit.Assert.assertEquals;

@DataMongoTest
@ExtendWith(SpringExtension.class)
public class PackingOrderSeptDefs {
    Order order;
    List<Order> orders;

    @Autowired
    MongoTemplate mongoTemplate;

    @After
    public void deleteOrder(){
        mongoTemplate.remove(order);
    }

    @Given("^an order with id (\\d+)$")
    public void an_order_with_id(int idOrder) throws Exception {
        order = new Order(idOrder);
        mongoTemplate.save(order);
    }

    @When("^: Klaus goes to the url warehouse/orders$")
    public void roger_order_the_item() throws Exception {
        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<List<Order>> response = restTemplate.exchange("http://localhost:" + 9002 + "/warehouse/orders", HttpMethod.GET, null, new ParameterizedTypeReference<List<Order>>(){});
        orders = response.getBody();

    }

    @Then("^: The server will respond with (\\d+) order with id (\\d+)$")
    public void a_new_order_with_the_item_has_been_added(int nbOrder, int idOrder) throws Exception {
        assertEquals(nbOrder,orders.size());
        assertEquals(idOrder,orders.get(0).getOrderId());
    }


}
