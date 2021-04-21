package triangle;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class EquilateralTriangleTest {

	@Test
	void testEquilateralTriangle() {
		EquilateralTriangle et1 = new EquilateralTriangle(1);
		EquilateralTriangle et2 = new EquilateralTriangle(5);
		EquilateralTriangle et3 = new EquilateralTriangle(15);
		
		assertEquals(1, et1.sideA);
		assertEquals(1, et1.sideB);
		assertEquals(1, et1.sideC);
		
		assertEquals(5, et2.sideA);
		assertEquals(5, et2.sideB);
		assertEquals(5, et2.sideC);
		
		assertEquals(15, et3.sideA);
		assertEquals(15, et3.sideB);
		assertEquals(15, et3.sideC);
	}

	@Test
	void testGetPerimeter() {
		EquilateralTriangle et1 = new EquilateralTriangle(1);
		EquilateralTriangle et2 = new EquilateralTriangle(5);
		EquilateralTriangle et3 = new EquilateralTriangle(15);
		
		assertEquals(3, et1.getPerimeter(), 0.000001);
		assertEquals(15, et2.getPerimeter(), 0.000001);
		assertEquals(45, et3.getPerimeter(), 0.000001);
	}
	
	@Test
	void testGetArea() {
		EquilateralTriangle et1 = new EquilateralTriangle(1);
		EquilateralTriangle et2 = new EquilateralTriangle(5);
		EquilateralTriangle et3 = new EquilateralTriangle(15);
		
		assertEquals(0.4330, et1.getArea(), 0.0001);
		assertEquals(10.8253, et2.getArea(), 0.0001);
		assertEquals(97.4278, et3.getArea(), 0.0001);
	}
}