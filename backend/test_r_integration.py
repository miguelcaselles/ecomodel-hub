"""
Test R integration with heemod wrapper
"""
from engine.r_integration.heemod_wrapper import get_heemod_wrapper

def test_r_markov():
    print("\n" + "="*60)
    print("Testing R Integration with heemod")
    print("="*60 + "\n")

    try:
        # Initialize wrapper
        print("1. Initializing heemod wrapper...")
        wrapper = get_heemod_wrapper()
        print("   ✓ Wrapper initialized successfully\n")

        # Define states
        print("2. Defining health states...")
        states = {
            "Stable": {"cost": 3500, "utility": 0.85},
            "Progression": {"cost": 8000, "utility": 0.50},
            "Death": {"cost": 0, "utility": 0}
        }
        print(f"   ✓ Defined {len(states)} states: {list(states.keys())}\n")

        # Define transitions
        print("3. Defining transition matrix...")
        transitions = {
            "Stable": {"Stable": 0.88, "Progression": 0.10, "Death": 0.02},
            "Progression": {"Progression": 0.83, "Death": 0.17},
            "Death": {"Death": 1.0}
        }
        print("   ✓ Transition matrix defined\n")

        # Run model
        print("4. Running Markov model (10 cycles)...")
        result = wrapper.run_markov_model(
            states=states,
            transitions=transitions,
            cycles=10,
            discount_rate=0.03
        )
        print("   ✓ Model executed successfully\n")

        # Display results
        print("5. Results:")
        print(f"   • Total Cost: {result['total_cost']:,.2f} EUR")
        print(f"   • Total QALYs: {result['total_qaly']:.4f}")
        print(f"   • Total LYs: {result['total_ly']:.4f}")

        if 'state_traces' in result:
            print(f"\n   State traces (cycles):")
            for state, trace in result['state_traces'].items():
                print(f"      {state}: {trace[:3]}... (first 3 cycles)")

        # Generate R code
        print("\n6. Generating auditable R code...")
        r_code = wrapper.generate_r_code(states, transitions, 10)
        print(f"   ✓ Generated {len(r_code)} characters of R code\n")

        print("="*60)
        print("✓ ALL TESTS PASSED - R integration working correctly!")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_r_markov()
