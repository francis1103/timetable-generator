export const mockTimetables = [
  {
    id: 'opt1',
    name: 'Option 1',
    status: 'pending',
    paretoScore: 0.92,
    objectives: {
      workload: 0.85,
      utilization: 0.90,
      preferences: 0.95
    },
    conflicts: 0,
    timetable: [
      { day: 'Monday', time: '9-11', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
      { day: 'Monday', time: '11-1', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      { day: 'Monday', time: '2-4', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
      { day: 'Tuesday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
      { day: 'Tuesday', time: '11-1', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
      { day: 'Wednesday', time: '9-11', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      { day: 'Wednesday', time: '2-4', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
      { day: 'Thursday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
      { day: 'Thursday', time: '11-1', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
      { day: 'Friday', time: '9-11', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
    ]
  },
  {
    id: 'opt2',
    name: 'Option 2',
    status: 'approved',
    paretoScore: 0.87,
    objectives: {
      workload: 0.80,
      utilization: 0.85,
      preferences: 0.90
    },
    conflicts: 0,
    timetable: [
      { day: 'Monday', time: '9-11', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
      { day: 'Monday', time: '11-1', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
      { day: 'Monday', time: '2-4', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      { day: 'Tuesday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
      { day: 'Tuesday', time: '11-1', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
      { day: 'Wednesday', time: '9-11', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
      { day: 'Wednesday', time: '2-4', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      { day: 'Thursday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
      { day: 'Thursday', time: '11-1', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
      { day: 'Friday', time: '9-11', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
    ]
  },
  {
    id: 'opt3',
    name: 'Option 3',
    status: 'pending',
    paretoScore: 0.85,
    objectives: {
      workload: 0.75,
      utilization: 0.80,
      preferences: 0.85
    },
    conflicts: 0,
    timetable: [
      { day: 'Monday', time: '9-11', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      { day: 'Monday', time: '11-1', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
      { day: 'Monday', time: '2-4', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
      { day: 'Tuesday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
      { day: 'Tuesday', time: '11-1', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      { day: 'Wednesday', time: '9-11', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
      { day: 'Wednesday', time: '2-4', subject: 'Mathematics', room: 'A101', faculty: 'Dr. Smith', students: 45 },
      { day: 'Thursday', time: '9-11', subject: 'Chemistry', room: 'D401', faculty: 'Dr. Brown', students: 40 },
      { day: 'Thursday', time: '11-1', subject: 'Physics', room: 'B203', faculty: 'Dr. Johnson', students: 38 },
      { day: 'Friday', time: '9-11', subject: 'Computer Science', room: 'C305', faculty: 'Dr. Williams', students: 52 },
    ]
  }
];

export const mockAnalytics = {
  facultyWorkload: [
    { name: 'Dr. Smith', hours: 12, maxHours: 16 },
    { name: 'Dr. Johnson', hours: 16, maxHours: 16 },
    { name: 'Dr. Williams', hours: 14, maxHours: 16 },
    { name: 'Dr. Brown', hours: 10, maxHours: 16 },
    { name: 'Dr. Davis', hours: 8, maxHours: 16 },
    { name: 'Dr. Miller', hours: 12, maxHours: 16 },
  ],
  roomUtilization: [
    { name: 'A101', capacity: 50, utilization: 85, bookings: 17 },
    { name: 'B203', capacity: 40, utilization: 72, bookings: 14 },
    { name: 'C305', capacity: 60, utilization: 90, bookings: 18 },
    { name: 'D401', capacity: 45, utilization: 65, bookings: 13 },
    { name: 'E502', capacity: 35, utilization: 78, bookings: 15 },
    { name: 'F603', capacity: 30, utilization: 60, bookings: 12 },
  ],
  studentIdleTime: 4.2,
  paretoTradeoffs: [
    { name: 'Workload', value: 0.8 },
    { name: 'Room Usage', value: 0.9 },
    { name: 'Student Pref', value: 0.7 },
  ]
};

export const mockUsers = {
  admin: {
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'admin'
  },
  faculty: {
    name: 'Dr. Smith',
    email: 'faculty@example.com',
    role: 'faculty',
    department: 'Computer Science',
    subjects: ['Mathematics', 'Computer Science'],
    availability: {
      Monday: true,
      Tuesday: true,
      Wednesday: false,
      Thursday: true,
      Friday: true
    }
  },
  student: {
    name: 'John Doe',
    email: 'student@example.com',
    role: 'student',
    year: 3,
    department: 'Computer Science',
    electives: ['AI', 'Data Science'],
    preferences: {
      morningClasses: true,
      noBackToBack: false,
      preferredDays: ['Monday', 'Tuesday', 'Wednesday']
    }
  }
};

export const mockAgents = {
  faculty: {
    response: "I'm satisfied with this schedule. My workload is balanced and I have no conflicts.",
    accepted: true,
    reason: ""
  },
  student: {
    response: "I like most of my classes, but I have a long gap on Tuesday. Can we adjust that?",
    accepted: false,
    reason: "Long gap between classes on Tuesday"
  },
  room: {
    response: "All room assignments are appropriate for the class sizes.",
    accepted: true,
    reason: ""
  },
  admin: {
    response: "Let's try to address the student's concern about the gap on Tuesday.",
    accepted: false,
    reason: "Student feedback on gap"
  }
};