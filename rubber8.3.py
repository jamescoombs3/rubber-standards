from manim import *
import scipy.stats as stats

class NormalDistributionAnimation(Scene):
    def construct(self):
        # ---------------------------------------------------------
        # 1. Heading and Subheading (with TM Symbol)
        # ---------------------------------------------------------
        # Using Tex to create superscript doesn't seem to work so create a 'tm' mobject and put next to the title. 
        title = Text(r"Rubber Standardisation", font_size=58).to_edge(UP, buff=0.5)
        subtitle = Text('Boost qualifying candidate numbers without changing the qualifying score', 
                        font_size=18, color=YELLOW, slant=ITALIC).next_to(title, DOWN, buff=0.2)

        header_group = VGroup(title, subtitle).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.4)

        tm = Text('TM', font_size=16 
            ).next_to(title, direction=RIGHT, buff=0.2).shift(UP * 0.2)

        self.play(FadeIn(header_group, shift=UP))

        tm = Text('TM', font_size=16 
            ).next_to(title, direction=RIGHT, buff=0.0).shift(UP * 0.2)
        self.play(FadeIn(tm))
        self.play(Flash(tm))

        # self.wait(0.5)   # The wiggle alread gives a half second pause here. 


        # ---------------------------------------------------------
        # 2. Initial Setup & Trackers
        # ---------------------------------------------------------
        init_mean = 100
        init_std = 15
        target_std = 90
        
        mean_tracker = ValueTracker(init_mean)
        std_tracker = ValueTracker(init_std)

        # ---------------------------------------------------------
        # 3. Configure Primary Axis (Z-score Framework)
        # ---------------------------------------------------------
        axes = Axes(
            x_range=[-3.5, 3.5, 1],
            y_range=[0, 0.45, 0.1],
            x_length=10,
            y_length=3.5,
            axis_config={"include_numbers": True, "font_size": 16},
            x_axis_config={"include_tip": False},  
            y_axis_config={"include_tip": False}   
        ).shift(UP * 0.2)
        


        # ---------------------------------------------------------
        # 3b. Re-engineered Stretching Secondary Axis (11-Plus Scores)
        # ---------------------------------------------------------
        # Instead of static z-steps mapping to texts, this redraws a true NumberLine
        # spanning the exact same physical space but with changing mathematical bounds.
        # MY CHANGES. Versions 8.1, 8.2 were prototypes of 'dynamic step splitting'. 
        # Also changed base step to 15 to match initial std deviations 
        def get_marks_axis():
            m = mean_tracker.get_value() # Always 100 in this scenario
            s = std_tracker.get_value()
            
            # --- 1. Dynamic Step Splitting Logic ---
            base_step = 15
            scale_factor = 2 ** int(np.log2(s / 15)) if s >= 15 else 1
            step_size = base_step * scale_factor

            # --- 2. Build the Core Axis Line ---
            axis_line = Line(
                axes.x_axis.number_to_point(-3.5),
                axes.x_axis.number_to_point(3.5),
                stroke_width=2,
                color=RED_A
            ).shift(DOWN * 0.6) # Kept close to the main axis

            axis_group = VGroup(axis_line)

            # --- 3. Symmetrical Ticks & Labels Generator ---
            # Instead of a left-to-right range, we start precisely at the center point (100)
            # and branch outward to guarantee complete visual symmetry.
            center_val = 100
            
            # Estimate how many steps we need to cover the viewport width (z = -3.5 to 3.5)
            # 4.5 standard deviations out ensures smooth entry/exit scrolling from off-screen
            max_val_coverage = 4.5 * s
            max_steps = int(max_val_coverage / step_size) + 2

            # Use a set to prevent duplicate handling of the center value (i = 0)
            processed_vals = set()

            for i in range(max_steps):
                # Generate matching pairs symmetrically stepping away from the center
                for sign in [1, -1]:
                    val = center_val + (sign * i * step_size)
                    
                    if val in processed_vals:
                        continue
                    processed_vals.add(val)

                    # Calculate the exact fractional Z-score for this numerical mark
                    z = (val - m) / s
                    
                    # Only render if the sliding coordinate is within view limits
                    if -3.5 <= z <= 3.5:
                        screen_x = axes.x_axis.number_to_point(z)
                        tick_position = [screen_x[0], axis_line.get_center()[1], 0]
                        
                        # Create the symmetrical tick line
                        tick = Line(
                            tick_position + UP * 0.1,
                            tick_position + DOWN * 0.1,
                            stroke_width=2,
                            color=RED_A
                        )
                        
                        # Render the corresponding text below the tick mark
                        label = Text(f"{val}", font_size=12, color=RED_A)
                        label.next_to(tick, DOWN, buff=0.1)
                        
                        axis_group.add(tick, label)

            return axis_group



        marks_axis_group = always_redraw(get_marks_axis)
        
        """
        # Google 8.3. This bit might need some tweaking. 
        # Static label positioning underneath the moving axis
        s_label = Text("11-plus scores", font_size=16, color=RED_A).move_to(
            axes.x_axis.number_to_point(0) + DOWN * 2.1
        )
        """
        # MY CHANGES to text and position ... although I haven't seen this text displayed anywhere !
        # axis_title = Text("Exam Marks Axis", font_size=16, color=YELLOW).next_to(marks_axis, DOWN, buff=0.4)
        axis_title = Text("11-plus scoreSSS", font_size=16, color=RED_A).next_to(axes.x_axis, DOWN, buff=-0.1)

        # z_label = Text("z-score", font_size=16, color=GRAY).next_to(axes.x_axis, DOWN, buff=0.2)
        # MY Change to the labels for the axes. 
        # NEED TO FIND THE s_label code and add correct place then remove this comment **************************************************
        #######################################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        z_label = Text("z-score", font_size=16, color=GRAY).next_to(axes.x_axis, DOWN, buff=-0.2)
        # s_label = Text('Rubber standardised test scores', font_size=16, color=RED_A).next_to(axes.x_axis, DOWN, buff=0.7)
        s_label = Text("Rubber Standardised scores", font_size=16, color=RED_A).next_to(axes.x_axis, DOWN, buff=0.7)

        self.play(Create(axes), Write(z_label))
        self.play(FadeIn(marks_axis_group), Write(s_label))


        # ---------------------------------------------------------
        # 4. Plot Normal Distribution & Shaded Area
        # ---------------------------------------------------------
        curve = axes.plot(
            lambda x: stats.norm.pdf(x, 0, 1),
            color=BLUE,
            use_smoothing=True
        )

        def get_shaded_area():
            m = mean_tracker.get_value()
            s = std_tracker.get_value()
            z_cutoff = (121 - m) / s
            
            start_z = max(z_cutoff, -3.5)
            if start_z >= 3.5:
                return VectorizedVMobject()
                
            return axes.get_area(curve, x_range=[start_z, 3.5], color=RED, opacity=0.5)

        shaded_area = always_redraw(get_shaded_area)

        self.play(Create(curve))
        self.play(FadeIn(shaded_area))

        # ---------------------------------------------------------
        # 5. Dynamic Vertical Line for Pass Mark (121)
        # ---------------------------------------------------------
        def get_indicator_line():
            m = mean_tracker.get_value()
            s = std_tracker.get_value()
            z_cutoff = (121 - m) / s
            
            x_point = axes.x_axis.number_to_point(z_cutoff)
            
            line = DashedLine(
                start=[x_point[0], axes.y_axis.number_to_point(0)[1], 0],
                end=[x_point[0], axes.y_axis.number_to_point(0.42)[1], 0],
                color=ORANGE,
                stroke_width=3
            )
            return line

        indicator_line = always_redraw(get_indicator_line)
        self.play(Create(indicator_line))

        # ---------------------------------------------------------
        # 6. Upper Left Stats Sidebar
        # ---------------------------------------------------------
        def get_stats_block():
            m = mean_tracker.get_value()
            s = std_tracker.get_value()
            z_cutoff = (121 - m) / s
            prob = 1 - stats.norm.cdf(z_cutoff)
            percentage = prob * 100
            
            line1 = Tex("Qualifying Score: 121", color=RED_A)
            line2 = Tex(f"Pass Rate: {percentage:.2f}\\%", color=WHITE)
            line3 = Tex(f"Std Dev: {s:.1f}", color=YELLOW)
            
            block = VGroup(line1, line2, line3).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
            block.set_font_size(36)
            block.to_corner(UL, buff=0.4).shift(DOWN * 1.5)
            return block

        stats_display = always_redraw(get_stats_block)
        self.play(Write(stats_display))

        # ---------------------------------------------------------
        # MY (BIG!) CHANGE
        # 7 This is where we add a hand drawn arrow and text. Putting this before the 1 sec wait and changing that 
        # to half a second. (This is where we break everything? Debugging runtime errors is hard!)
        # ---------------------------------------------------------
        # 7.1 Define precise hand-drawn arrow using your object's coordinates
        hand_arrow = ArcBetweenPoints(
            start=shaded_area.get_top() + LEFT * 0.2 + UP * 0.2, # Adjust start position
            end=shaded_area.get_top() + LEFT * 0.75 + DOWN * 0.75,               # Points just above target
            angle=-TAU / 6,                                            # Slight organic bend
            color=RED,
            stroke_width=4
        ).add_tip(tip_shape=StealthTip,  # Swap the head style here!
                  tip_length=0.3,                
                  tip_width=0.15
                  )

        # 7.2 Add handwritten looking text (thanks Google for the font.) 
        hand_text = Text(
            'Candidates\nthat "passed"', 
            font="Caveat",
            font_size=36, 
            color=RED
        ).next_to(hand_arrow.get_start(), UP, buff=0.1).shift(UP * 0.1)

        # 7.3 Rotate 10 degrees anti-clockwise
        hand_text.rotate(10 * DEGREES)

        # 7.4 Animate them sequentially
        self.play(Create(hand_arrow), run_time=0.8)
        self.play(Write(hand_text), run_time=0.6)

        # 7.5 MY small CHANGE next line from one to half a second. 
        self.wait(0.5)

        
        # ---------------------------------------------------------
        # 8. Run Animation Sequence
        # ---------------------------------------------------------
        # Moving Std Dev up to 90 automatically causes the NumberLine bounds 
        # to shift outwards, pushing initial ticks off-screen while bringing new increments into view.
        self.play(
            std_tracker.animate.set_value(target_std),
            run_time=20,
            rate_func=smooth
        )
        s_print = Text('Call 1-800-dial-a-cohort for free quotation', font_size=10, color=RED_A).to_corner(DR)  # Bottom Right
        self.add(s_print)
        self.wait(2)