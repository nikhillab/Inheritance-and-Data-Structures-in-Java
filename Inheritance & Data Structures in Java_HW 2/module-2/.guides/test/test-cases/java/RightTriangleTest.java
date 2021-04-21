package triangle;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class RightTriangleTest {

	@Test
	void testRightTriangle() {
		
		RightTriangle rt1 = new RightTriangle(1, 1);
		RightTriangle rt2 = new RightTriangle(2, 2);
		RightTriangle rt3 = new RightTriangle(1, 3);
		
		assertEquals(1, rt1.sideA);
		assertEquals(1, rt1.sideB);
		assertEquals(1.4142, rt1.sideC, 0.0001);
		assertEquals(2, rt2.sideA);
		assertEquals(2, rt2.sideB);
		assertEquals(2.8284, rt2.sideC, 0.0001);
		assertEquals(1, rt3.sideA);
		assertEquals(3, rt3.sideB);
		assertEquals(3.1622, rt3.sideC, 0.0001);
	}

	@Test
	void testGetPerimenter() {
		RightTriangle rt1 = new RightTriangle(1, 1);
		RightTriangle rt2 = new RightTriangle(2, 2);
		RightTriangle rt3 = new RightTriangle(1, 3);
		
		assertEquals(3.4142, rt1.getPerimeter(), 0.0001);
		assertEquals(6.8284, rt2.getPerimeter(), 0.0001);
		assertEquals(7.1622, rt3.getPerimeter(), 0.0001);
	}
	
	@Test
	void testGetArea() {
		
		RightTriangle rt1 = new RightTriangle(1, 1);
		RightTriangle rt2 = new RightTriangle(2, 2);
		RightTriangle rt3 = new RightTriangle(1, 3);
		
		assertEquals(0.5, rt1.getArea(), 0.0001);
		assertEquals(2, rt2.getArea(), 0.0001);
		assertEquals(1.5, rt3.getArea(), 0.0001);
	}
}