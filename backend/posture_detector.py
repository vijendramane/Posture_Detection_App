
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional
import  math 
 
 
class PostureDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def calculate_angle(self, a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def extract_keypoints(self, image: np.ndarray) -> Optional[Dict]:
        """Extract pose keypoints from image"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            keypoints = {}
            
            # Extract key body points
            keypoints['nose'] = (landmarks[self.mp_pose.PoseLandmark.NOSE.value].x,
                               landmarks[self.mp_pose.PoseLandmark.NOSE.value].y)
            keypoints['left_shoulder'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y)
            keypoints['right_shoulder'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                         landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)
            keypoints['left_hip'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y)
            keypoints['right_hip'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y)
            keypoints['left_knee'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y)
            keypoints['right_knee'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y)
            keypoints['left_ankle'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                     landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y)
            keypoints['right_ankle'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y)
            keypoints['left_foot_index'] = (landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                                          landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y)
            keypoints['right_foot_index'] = (landmarks[self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,
                                           landmarks[self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y)
            
            return keypoints
        return None
    
    def analyze_squat_posture(self, keypoints: Dict) -> Dict:
        """Analyze squat posture and detect bad form"""
        issues = []
        angles = {}
        
        # Calculate knee-over-toe for both legs
        left_knee_over_toe = keypoints['left_knee'][0] > keypoints['left_foot_index'][0]
        right_knee_over_toe = keypoints['right_knee'][0] > keypoints['right_foot_index'][0]
        
        if left_knee_over_toe or right_knee_over_toe:
            issues.append("Knee tracking over toe - keep knees aligned with ankles")
        
        # Calculate back angle (shoulder-hip-knee)
        # Use the more visible side
        left_back_angle = self.calculate_angle(
            keypoints['left_shoulder'],
            keypoints['left_hip'],
            keypoints['left_knee']
        )
        right_back_angle = self.calculate_angle(
            keypoints['right_shoulder'],
            keypoints['right_hip'],
            keypoints['right_knee']
        )
        
        back_angle = max(left_back_angle, right_back_angle)
        angles['back_angle'] = back_angle
        
        if back_angle < 150:
            issues.append(f"Back too curved (angle: {back_angle:.1f}°) - keep back straighter")
        
        # Check knee angle for depth
        left_knee_angle = self.calculate_angle(
            keypoints['left_hip'],
            keypoints['left_knee'],
            keypoints['left_ankle']
        )
        right_knee_angle = self.calculate_angle(
            keypoints['right_hip'],
            keypoints['right_knee'],
            keypoints['right_ankle']
        )
        
        knee_angle = min(left_knee_angle, right_knee_angle)
        angles['knee_angle'] = knee_angle
        
        if knee_angle > 120:
            issues.append(f"Squat not deep enough (knee angle: {knee_angle:.1f}°)")
        
        return {
            'posture_type': 'squat',
            'issues': issues,
            'angles': angles,
            'is_good_posture': len(issues) == 0
        }
    
    def analyze_sitting_posture(self, keypoints: Dict) -> Dict:
        """Analyze sitting posture and detect bad form"""
        issues = []
        angles = {}
        
        # Calculate neck bend angle (nose-shoulder alignment)
        # Use average of both shoulders
        avg_shoulder_x = (keypoints['left_shoulder'][0] + keypoints['right_shoulder'][0]) / 2
        avg_shoulder_y = (keypoints['left_shoulder'][1] + keypoints['right_shoulder'][1]) / 2
        
        # Calculate neck forward angle
        neck_forward_distance = abs(keypoints['nose'][0] - avg_shoulder_x)
        neck_vertical_distance = abs(keypoints['nose'][1] - avg_shoulder_y)
        
        if neck_vertical_distance > 0:
            neck_angle = math.degrees(math.atan(neck_forward_distance / neck_vertical_distance))
            angles['neck_angle'] = neck_angle
            
            if neck_angle > 30:
                issues.append(f"Neck too forward (angle: {neck_angle:.1f}°) - pull head back")
        
        # Check back straightness (shoulder-hip alignment)
        avg_hip_x = (keypoints['left_hip'][0] + keypoints['right_hip'][0]) / 2
        back_lean_distance = abs(avg_shoulder_x - avg_hip_x)
        
        if back_lean_distance > 0.1:  # Threshold for back straightness
            issues.append("Back not straight - sit up straighter")
        
        # Check shoulder level
        shoulder_height_diff = abs(keypoints['left_shoulder'][1] - keypoints['right_shoulder'][1])
        if shoulder_height_diff > 0.05:  # Threshold for shoulder alignment
            issues.append("Shoulders not level - balance your posture")
        
        return {
            'posture_type': 'sitting',
            'issues': issues,
            'angles': angles,
            'is_good_posture': len(issues) == 0
        }
    
    def analyze_posture(self, image: np.ndarray, posture_type: str = 'sitting') -> Dict:
        """Main function to analyze posture from image"""
        keypoints = self.extract_keypoints(image)
        
        if keypoints is None:
            return {
                'error': 'No pose detected in image',
                'keypoints': None,
                'analysis': None
            }
        
        # Analyze based on posture type
        if posture_type == 'squat':
            analysis = self.analyze_squat_posture(keypoints)
        else:  # Default to sitting
            analysis = self.analyze_sitting_posture(keypoints)
        
        return {
            'keypoints': keypoints,
            'analysis': analysis,
            'timestamp': None
        }
    
    def draw_pose_landmarks(self, image: np.ndarray, keypoints: Dict) -> np.ndarray:
        """Draw pose landmarks on image"""
        height, width = image.shape[:2]
        
        # Convert normalized coordinates to pixel coordinates
        pixel_keypoints = {}
        for key, (x, y) in keypoints.items():
            pixel_keypoints[key] = (int(x * width), int(y * height))
        
        # Draw keypoints
        for point in pixel_keypoints.values():
            cv2.circle(image, point, 5, (0, 255, 0), -1)
        
        # Draw connections
        connections = [
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            ('left_hip', 'left_knee'),
            ('right_hip', 'right_knee'),
            ('left_knee', 'left_ankle'),
            ('right_knee', 'right_ankle'),
            ('nose', 'left_shoulder'),
            ('nose', 'right_shoulder')
        ]
        
        for start, end in connections:
            if start in pixel_keypoints and end in pixel_keypoints:
                cv2.line(image, pixel_keypoints[start], pixel_keypoints[end], (255, 0, 0), 2)
        
        return image
