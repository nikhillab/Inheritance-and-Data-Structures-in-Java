package transportation;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class VehicleTest {
	Vehicle jeep1;
	Vehicle jeep2;
	Vehicle benz;
	Vehicle bike1;
	Vehicle bike2;
	Vehicle bike3;
	
	@BeforeEach
	void setUp() throws Exception {
		this.jeep1 = new Car("Jeep", 2019);
		this.jeep2 = new Car("Jeep", 2010);
		this.benz = new Car("Benz", 2020);
		this.bike1 = new Bike("Trek", 1999);
		this.bike2 = new Bike("Giant", 1999);
		this.bike3 = new Bike("Giant", 2020);
	}

	@Test
	void testVehicle() {
		assertEquals(jeep1.brand, "Jeep");
		assertEquals(jeep2.brand, "Jeep");
		assertEquals(benz.brand, "Benz");
		assertEquals(bike1.brand, "Trek");
		assertEquals(bike2.brand, "Giant");
		assertEquals(bike3.brand, "Giant");
		
		assertEquals(jeep1.type, "Car");
		assertEquals(jeep2.type, "Car");
		assertEquals(benz.type, "Car");
		assertEquals(bike1.type, "Bike");
		assertEquals(bike2.type, "Bike");
		assertEquals(bike3.type, "Bike");
		
	}

	@Test
	void testGetAge() {
		assertEquals(jeep1.getAge(), 1);
		assertEquals(jeep2.getAge(), 10);
		assertEquals(benz.getAge(), 0);
		assertEquals(bike1.getAge(), 21);
		assertEquals(bike2.getAge(), 21);
		assertEquals(bike3.getAge(), 0);
	}

	@Test
	void testGetGasRemained() {
		bike1.refuel(100);
		assertEquals(bike1.getGasRemained(), 0);
		bike1.refuel(10000);
		assertEquals(bike1.getGasRemained(), 0);
		jeep1.refuel(1);
		assertEquals(jeep1.getGasRemained(), 1);
		jeep1.refuel(100);
		assertEquals(jeep1.getGasRemained(), 101);
		jeep1.refuel(300);
		assertEquals(jeep1.getGasRemained(), 200);
	}
	
	@Test
	void testGetTotalGasConsumed() {
		bike2.run(100);
		bike2.run(100);
		bike2.run(100);
		assertEquals(bike1.getTotalGasConsumed(), 0);
		benz.run(10);
		
		assertEquals(benz.getTotalGasConsumed(), 0);
		benz.refuel(100);
		benz.run(5);
		benz.run(5);
		assertEquals(benz.getTotalGasConsumed(), 100);
		benz.refuel(200);
		benz.run(25);
		assertEquals(benz.getTotalGasConsumed(), 300);
		
		jeep1.refuel(200);
		jeep1.run(10);
		assertEquals(jeep1.getTotalGasConsumed(), 100);
		jeep1.run(15);
		assertEquals(jeep1.getTotalGasConsumed(), 200);
		jeep1.refuel(100);
		assertEquals(jeep1.getTotalGasConsumed(), 200);
		
	}

	@Test
	void testRefuel() {
		bike1.refuel(100);
		assertEquals(bike1.getGasRemained(), 0);
		
		jeep1.refuel(100);
		assertEquals(jeep1.getGasRemained(), 100);
		jeep1.refuel(101);
		assertEquals(jeep1.getGasRemained(), 200);
		
		// TODO write at least 3 additional test cases 
		
	}
	
	@Test
	void testRun() {
		bike2.run(100);
		bike2.run(100);
		bike2.run(100);
		assertEquals(bike1.getGasRemained(), 0);
		
		benz.run(10);
		assertEquals(benz.getGasRemained(), 0);
		benz.refuel(100);
		benz.run(5);
		assertEquals(benz.getGasRemained(), 50);
		
		// TODO write at least 3 additional test cases 
        bike2.run(100);
		bike2.run(100);
		bike2.run(100);
		assertEquals(bike1.getGasRemained(), 0);
		
		benz.run(10);
		assertEquals(benz.getGasRemained(), 0);
		benz.refuel(100);
		benz.run(5);
		assertEquals(benz.getGasRemained(), 50);
	}

	@Test
	void testEquals() {
		assertTrue(jeep1.equals(jeep2));
		assertFalse(benz.equals(jeep2));

		// TODO write at least 3 additional test cases 
        	assertFalse(benz.equals(bike1));
		assertFalse(bike2.equals(jeep2));
		assertFalse(benz.equals(bike3));
	}

	@Test
	void testToString() {
		assertEquals(jeep1.toString(), "Car Jeep");
		assertEquals(bike1.toString(), "Bike Trek");
		
		// TODO write at least 3 additional test cases 
        
		assertEquals(bike2.toString(), "Bike Giant");
		assertEquals(jeep2.toString(), "Car Jeep");
		assertEquals(bike3.toString(), "Bike Giant");
		
	}
}